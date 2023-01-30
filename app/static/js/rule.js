window.onload = function() {
    update_input_hw_selectbox(document.getElementById('select_input_hw'));
    update_output_hw_selectbox(document.getElementById('select_output_hw'));
}

document.addEventListener('DOMContentLoaded', function() {
    check_selectbox();
}, false);

function check_selectbox() {
    // input_hwのセレクトボックス変更時
    let input_hw = document.getElementById('select_input_hw');
    input_hw.addEventListener('change', function() {
        //console.log('input change')
        update_input_hw_selectbox(input_hw);
    }, false);

    // output_hwのセレクトボックス変更時
    let output_hw = document.getElementById('select_output_hw');
    output_hw.addEventListener('change', function() {
        //console.log('output change')
        update_output_hw_selectbox(output_hw);
    }, false);
}

function update_input_hw_selectbox(input_hw) {
    // 本来であれば機材タイプを調べるべきだが、仮で名前から判定する
    let item = input_hw.value;
    if (item.startsWith('dht11-post-')) {
        // 温湿度センサー 
        input_hw_option_view('temp');
    } else if (item.startsWith('image-send-app')) {
        // camera
        input_hw_option_view('image-send-app');
    }
}

function update_output_hw_selectbox(output_hw) {
    // 本来であれば機材タイプを調べるべきだが、仮で名前から判定する
    let item = output_hw.value;
    //console.log(item)
    if (item.indexOf('remote') > -1) {
        output_hw_option_view('remote')
            //console.log('remote')
    } else if (item.indexOf('discord') > -1) {
        output_hw_option_view('discord')
            //console.log('dc')
    }
}


function input_hw_option_view(type) {
    switch (type) {
        case 'temp':
            sel = document.getElementById('select_kind')
            while (0 < sel.childNodes.length) {
                sel.removeChild(sel.childNodes[0]);
            }
            // option要素を追加
            display_element('kind', true)
            append_option(sel, 'temp_upper')
            append_option(sel, 'temp_under')
            append_option(sel, 'hum_upper')
            append_option(sel, 'hum_under')
            break
        case 'image-send-app':
            sel = document.getElementById('select_kind')
            while (0 < sel.childNodes.length) {
                sel.removeChild(sel.childNodes[0]);
            }
            display_element('kind', false)
            break
        default:
            console.log(nil)
    }
}

function output_hw_option_view(type) {
    switch (type) {
        case 'remote':
            display_element('outhw_opt_path', true)
            display_element('outhw_opt', true)
            display_element('outhw_opt_remotename', true)
            display_element('outhw_opt_remotefunction', true)
            break
        case 'discord':
            display_element('outhw_opt_path', false)
            display_element('outhw_opt', true)
            display_element('outhw_opt_remotename', true)
            display_element('outhw_opt_remotefunction', false)
            break
        default:
            console.log(nil)
    }
}

function append_option(sel, value) {
    let opt = document.createElement('option');
    opt.appendChild(document.createTextNode(value));
    //opt.appendChild(document.create)
    sel.appendChild(opt);
}

function display_element(elm_id, f) {
    if (f == true) {
        document.getElementById(elm_id).style.display = "block";
    } else {
        document.getElementById(elm_id).style.display = "none";
    }
}