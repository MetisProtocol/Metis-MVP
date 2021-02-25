function _post(url, data, callback) {
    var loading;

    $.ajax({
        url: url,
        data: data,
        type: "POST",
        beforeSend: function () {
            loading = weui.loading("");
        },
        success: function (resp) {
            callback(resp);
        },
        complete: function () {
            if (loading) {
                loading.hide();
            }
        }
    })
}

function _get(url, data, callback) {
    var loading;

    $.ajax({
        url: url,
        data: data,
        type: "GET",
        beforeSend: function () {
            loading = weui.loading("加载中");
        },
        success: function (resp) {
            callback(resp);
        },
        complete: function () {
            if (loading) {
                // loading.hide();
            }
        }
    })
}

function _delete(url, data, callback) {
    var loading;

    $.ajax({
        url: url,
        data: data,
        type: "DELETE",
        beforeSend: function () {
            loading = weui.loading("删除中");
        },
        success: function (resp) {
            callback(resp);
        },
        complete: function () {
            if (loading) {
                loading.hide();
            }
        }
    })
}

function _put(url, data, callback) {
    var loading;

    $.ajax({
        url: url,
        data: data,
        type: "PUT",
        beforeSend: function () {
            loading = weui.loading("保存中");
        },
        success: function (resp) {
            callback(resp);
            callback(resp);
        },
        complete: function () {
            if (loading) {
                loading.hide();
            }
        }
    })
}

// function tip(message) {
//     let body = $("body");
//     body.find(".toast").remove();
//     $('<div class="toast"> <div class="text">' + message + '</div> </div>').appendTo(body);
//     $.fancybox.open($(".toast"), {
//         'smallBtn': false
//     });
// }
function tip(message) {
    let M = {};
    if(M.dialog1){
			return M.dialog1.show();
		}
		M.dialog1 = jqueryAlert({
			'content' : message,
			'closeTime' : 2000
		})
}

function _switch_menu(id){
    // all menus
    let lis = $("[id='_menu']").find('li');

    // remove all li active class
    $.each(lis, function(index, item){
        $(item).removeClass("active");
    });

    // add active class for spec menu li 'id'
    $("[id='" + id + "']").addClass("active")
}

function _switch_sub_menu(nav_li_element_id, sub_id){
    let ul_element_id = "[id='_sub" + nav_li_element_id + "']";
    let lis = $(ul_element_id).find('li');

    $.each(lis, function(index, item){
            $(item).removeClass("active")
        }
    );

    $("[id='" + nav_li_element_id + "']").addClass("active menu-open");
    $("[id='" + sub_id + "']").addClass("active");
}

function _notify(append_element_id, notify_content, notify_type) {
    // css 样式需要提前定义好
    let parent = $("[id='" + append_element_id + "']");
    let notify = document.createElement('div');
    let content = document.createElement("div");
    let notify_icon_div = document.createElement("div");
    notify_icon_div.className = "iq-alert-icon";
    let notify_icon = document.createElement("i");
    notify_icon.className = "ri-information-line";
    content.className = "iq-alert-text";
    content.textContent = notify_content;
    if(notify_type === 'success') {
        notify.className = "alert text-block-50 bg-success";
        notify_icon.className = "ri-information-line";
    }
    else if (notify_type === 'error') {
        notify.className = "alert text-block-50 bg-danger";
        notify_icon.className = "ri-alert-line";
    }
    notify_icon_div.append(notify_icon);
    notify.append(notify_icon_div);
    notify.append(content);
    parent.append(notify);
}

function _remove_notify(id) {
    let notify_nodes = document.getElementById(id).childNodes;
    for (let i=0; i<notify_nodes.length; i++){
        document.getElementById(id).removeChild(notify_nodes[i]);
    }
}

function fresh_redirect(next_url, delay) {
    window.setTimeout(
        function () {
            window.location.href = next_url;
        },
        delay
    )
}

// build sweet alert  pre import sweetalert.css & sweetalert.js

function _sweet_alert_notify(type, title, content) {
    swal(title, content, type);
}

function _sweet_alert_with_buttons(title, content, type, confirmButtonText, cancelButtonText, callback) {
    swal(
        {
            title: title,
            text: content,
            type: type,
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: "#d33",
            confirmButtonText: cancelButtonText,
            cancelButtonText: confirmButtonText,
            confirmButtonClass: "btn btn-danger button-margin i18n",
            cancelButtonClass: "btn btn-success button-margin i18n",
            buttonsStyling: false
        }).then(
            callback
    );
}

function _fresh_current_page(delay) {
    if (delay === null|| delay === undefined){
        delay = 1500;
    }
    window.setTimeout(
        function () {
            window.location.reload();
        },
        delay
    );
}
