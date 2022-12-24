/**
 * File related functions *********************************************************
 */
let fileHandle;
let date;
var butOpenFile = document.getElementById("inputfile")
butOpenFile.addEventListener('click', async () => {
    [fileHandle] = await window.showOpenFilePicker();
    const file = await fileHandle.getFile();
    const content = await file.text()
    // write table
    data = JSON.parse(content);
    data2table();

    document.getElementById('filename').innerHTML = fileHandle.name;
    document.title = fileHandle.name
});

async function writeFile(fileHandle, contents) {
    // Create a FileSystemWritableFileStream to write to.
    const writable = await fileHandle.createWritable();
    // Write the contents of the file to the stream.
    await writable.write(contents);
    // Close the file and write the contents to disk.
    await writable.close();
}

function download(data, filename, type) {
    // Function to download data to a file
    console.log(data)
    var file = new Blob([data], { type: type });
    if (window.navigator.msSaveOrOpenBlob) // IE10+
        window.navigator.msSaveOrOpenBlob(file, filename);
    else { // Others
        var a = document.createElement("a"),
            url = URL.createObjectURL(file);
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        setTimeout(function () {
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        }, 0);
    }
}


function save() {
    table2data();
    text = JSON.stringify(data, null, 2)
    writeFile(fileHandle, text);
}

function save_code() {
    table2data()
    text = JSON.stringify(data, null, 2)
    try {
        download(text, fileHandle.name, 'text')
    } catch {
        download(text, 'settings.json', 'text')
    }
}

/**
 * CSV
 */

function data2table() {
    var table = document.getElementById('display');
    table.style = ''
    table.innerHTML = '';

    var layer_keys = Object.keys(data).sort()
    var macro_keys = Object.keys(data['-1']).sort()
    for (var i=0; i<layer_keys.length; i++) {
        console.log(layer_keys[i])
        var l_title = document.createElement('h3')
        l_title.id = 'layer_' + layer_keys[i]
        l_title.innerHTML = 'Layer ' + layer_keys[i]
        if (layer_keys[i] === '-1') {
            l_title.innerHTML += ' (default)'
        }
        table.appendChild(l_title)
        for (var j=0; j<macro_keys.length; j++){
            console.log(macro_keys[j], data[layer_keys[i]][macro_keys[j]])
            var m_line = document.createElement('p')
            table.appendChild(m_line)

            var m_title = document.createElement('b')
            m_title.innerHTML = 'key ' + macro_keys[j] + ': '

            var m_name_title = document.createElement('text')
            m_name_title.innerHTML = 'name:'

            var m_name = document.createElement('input')
            m_name.setAttribute("type", "text");
            m_name.id = 'name_' + layer_keys[i] + '_' + macro_keys[j]
            m_name.value = data[layer_keys[i]][macro_keys[j]][0]

            var m_macro_title = document.createElement('text')
            m_macro_title.innerHTML = 'macro:'

            var m_macro = document.createElement('input')
            m_macro.setAttribute("type", "text");
            m_macro.setAttribute("size", 100);
            m_macro.id = 'macro_' + layer_keys[i] + '_' + macro_keys[j]
            m_macro.value = data[layer_keys[i]][macro_keys[j]][1]
            
            m_line.appendChild(m_title)

            m_line.appendChild(m_name_title)
            m_line.appendChild(m_name)
            
            m_line.appendChild(m_macro_title)
            m_line.appendChild(m_macro)
        }
    }
}

function table2data() {
    var layer_keys = Object.keys(data).sort()
    var macro_keys = Object.keys(data['-1']).sort()
    var cur_table = {}
    for (var i=0; i<layer_keys.length; i++) {
        var cur_layer = {}
        for (var j=0; j<macro_keys.length; j++){
            m_name_id = 'name_' + layer_keys[i] + '_' + macro_keys[j]
            m_macro_id = 'macro_' + layer_keys[i] + '_' + macro_keys[j]
            var cur_macro = [
                document.getElementById(m_name_id).value,
                document.getElementById(m_macro_id).value,
            ]
            cur_layer[macro_keys[j]] = cur_macro
        }
        cur_table[layer_keys[i]] = cur_layer
    }
    console.log(cur_table)
    data = cur_table
}