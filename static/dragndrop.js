/**
 * Created by a1 on 17.02.16.
 * скрипт отвечает за загрузку документов, которые переводятся мышкой в браузер (технология DragnDrop of files in browsers
 * основной код взят отсюда - https://habrahabr.ru/post/125424/
 */

var method_list = ["cluster", "cure", "classification", "neuron"];

$(document).ready(function() {
    var dropZone = $('#dropZone_' + 'cluster'),
        maxFileSize = 1000000; // максимальный размер файла - 1 мб.

    // Проверка поддержки браузером
    if (typeof(window.FileReader) == 'undefined') {
        dropZone.text('Не поддерживается браузером!');
        dropZone.addClass('error');
    }

    // Добавляем класс hover при наведении
    dropZone[0].ondragover = function () {
        dropZone.addClass('hover');
        return false;
    };

    // Убираем класс hover
    dropZone[0].ondragleave = function () {
        dropZone.removeClass('hover');
        return false;
    };

    // Обрабатываем событие Drop
    dropZone[0].ondrop = function (event) {
        event.preventDefault();
        dropZone.removeClass('hover');
        dropZone.addClass('drop');

        var afile = event.dataTransfer.files[0];

        var fd = new FormData();
        fd.append('file', afile);
        fd.append('method', "kmeans");
        $.ajax({
                xhr: function () {
                    var xhr = new window.XMLHttpRequest();
                    xhr.upload.addEventListener("progress", function (evt) {
                        if (evt.lengthComputable) {
                            var percentComplete = evt.loaded / evt.total;
                            dropZone.text('Загрузка: ' + parseInt(percentComplete * 100) + '%');
                        }
                    }, false);

                    xhr.addEventListener("progress", function (evt) {
                        if (evt.lengthComputable) {
                            var percentComplete = evt.loaded / evt.total;
                            dropZone.text('Загрузка: ' + percentComplete + '%');
                        }
                    }, false);

                    return xhr;
                },
                url: "http://" + host_url + port_url + "/file/upload",
                method: "POST",
                error: error,
                success: answerUpload,
                data: fd,
                processData: false,
                contentType: false
            }
        );


    };

    var answerUpload = function answerUpload(data) {
        filename = data;
        dropZone.removeClass('drop');
        dropZone.text("Загружено");
        window.location = "http://" + host_url + port_url + "/file/download?filename=" + filename;
        dropZone.text("Кластерный анализ (k-средних)");
        //$.ajax({
        //    url: "http://" + host_url + port_url + "/file/download",
        //    data: {"filename": data},
        //    method: "GET"
        //});
    };
    var error = function error(data) {
        $("#text_area").text("Произошла ошибка! " + data);
    }

});

$(document).ready(function() {
    var dropZone = $('#dropZone_' + 'cure'),
        maxFileSize = 1000000; // максимальный размер файла - 1 мб.

    // Проверка поддержки браузером
    if (typeof(window.FileReader) == 'undefined') {
        dropZone.text('Не поддерживается браузером!');
        dropZone.addClass('error');
    }

    // Добавляем класс hover при наведении
    dropZone[0].ondragover = function () {
        dropZone.addClass('hover');
        return false;
    };

    // Убираем класс hover
    dropZone[0].ondragleave = function () {
        dropZone.removeClass('hover');
        return false;
    };

    // Обрабатываем событие Drop
    dropZone[0].ondrop = function (event) {
        event.preventDefault();
        dropZone.removeClass('hover');
        dropZone.addClass('drop');

        var afile = event.dataTransfer.files[0];

        var fd = new FormData();
        fd.append('file', afile);
        fd.append('method', "cure");
        $.ajax({
                xhr: function () {
                    var xhr = new window.XMLHttpRequest();
                    xhr.upload.addEventListener("progress", function (evt) {
                        if (evt.lengthComputable) {
                            var percentComplete = evt.loaded / evt.total;
                            dropZone.text('Загрузка: ' + parseInt(percentComplete * 100) + '%');
                        }
                    }, false);

                    xhr.addEventListener("progress", function (evt) {
                        if (evt.lengthComputable) {
                            var percentComplete = evt.loaded / evt.total;
                            dropZone.text('Загрузка: ' + percentComplete + '%');
                        }
                    }, false);

                    return xhr;
                },
                url: "http://" + host_url + port_url + "/file/upload",
                method: "POST",
                error: error,
                success: answerUpload,
                data: fd,
                processData: false,
                contentType: false
            }
        );


    };

    var answerUpload = function answerUpload(data) {
        $("#text_area").text(data);
        dropZone.removeClass('drop');
        dropZone.text("Загружено");
        window.location = "http://" + host_url + port_url + "/file/download?filename=" + filename;
        dropZone.text("Кластерный анализ (CURE)");
    };
    var error = function error(data) {
        $("#text_area").text("Произошла ошибка! " + data);
    }

});

$(document).ready(function() {
    var dropZone = $('#dropZone_' + 'classification'),
        maxFileSize = 1000000; // максимальный размер файла - 1 мб.

    // Проверка поддержки браузером
    if (typeof(window.FileReader) == 'undefined') {
        dropZone.text('Не поддерживается браузером!');
        dropZone.addClass('error');
    }

    // Добавляем класс hover при наведении
    dropZone[0].ondragover = function () {
        dropZone.addClass('hover');
        return false;
    };

    // Убираем класс hover
    dropZone[0].ondragleave = function () {
        dropZone.removeClass('hover');
        return false;
    };

    // Обрабатываем событие Drop
    dropZone[0].ondrop = function (event) {
        event.preventDefault();
        dropZone.removeClass('hover');
        dropZone.addClass('drop');

        var afile = event.dataTransfer.files[0];

        var fd = new FormData();
        fd.append('file', afile);
        fd.append('method', "classification");
        $.ajax({
                xhr: function () {
                    var xhr = new window.XMLHttpRequest();
                    xhr.upload.addEventListener("progress", function (evt) {
                        if (evt.lengthComputable) {
                            var percentComplete = evt.loaded / evt.total;
                            dropZone.text('Загрузка: ' + parseInt(percentComplete * 100) + '%');
                        }
                    }, false);

                    xhr.addEventListener("progress", function (evt) {
                        if (evt.lengthComputable) {
                            var percentComplete = evt.loaded / evt.total;
                            dropZone.text('Загрузка: ' + percentComplete + '%');
                        }
                    }, false);

                    return xhr;
                },
                url: "http://" + host_url + port_url + "/file/upload",
                method: "POST",
                error: error,
                success: answerUpload,
                data: fd,
                processData: false,
                contentType: false
            }
        );


    };

    var answerUpload = function answerUpload(data) {
        $("#text_area").text(data);
        dropZone.removeClass('drop');
        dropZone.text("Загружено");
        window.location = "http://" + host_url + port_url + "/file/download?filename=" + filename;
        dropZone.text("Классификация");
    };
    var error = function error(data) {
        $("#text_area").text("Произошла ошибка! " + data);
    }

});

$(document).ready(function() {
    var dropZone = $('#dropZone_' + 'neuron'),
        maxFileSize = 1000000; // максимальный размер файла - 1 мб.

    // Проверка поддержки браузером
    if (typeof(window.FileReader) == 'undefined') {
        dropZone.text('Не поддерживается браузером!');
        dropZone.addClass('error');
    }

    // Добавляем класс hover при наведении
    dropZone[0].ondragover = function () {
        dropZone.addClass('hover');
        return false;
    };

    // Убираем класс hover
    dropZone[0].ondragleave = function () {
        dropZone.removeClass('hover');
        return false;
    };

    // Обрабатываем событие Drop
    dropZone[0].ondrop = function (event) {
        event.preventDefault();
        dropZone.removeClass('hover');
        dropZone.addClass('drop');

        var afile = event.dataTransfer.files[0];

        var fd = new FormData();
        fd.append('file', afile);
        fd.append('method', "neuron");
        $.ajax({
                xhr: function () {
                    var xhr = new window.XMLHttpRequest();
                    xhr.upload.addEventListener("progress", function (evt) {
                        if (evt.lengthComputable) {
                            var percentComplete = evt.loaded / evt.total;
                            dropZone.text('Загрузка: ' + parseInt(percentComplete * 100) + '%');
                        }
                    }, false);

                    xhr.addEventListener("progress", function (evt) {
                        if (evt.lengthComputable) {
                            var percentComplete = evt.loaded / evt.total;
                            dropZone.text('Загрузка: ' + percentComplete + '%');
                        }
                    }, false);

                    return xhr;
                },
                url: "http://" + host_url + port_url + "/file/upload",
                method: "POST",
                error: error,
                success: answerUpload,
                data: fd,
                processData: false,
                contentType: false
            }
        );


    };

    var answerUpload = function answerUpload(data) {
        $("#text_area").text(data);
        dropZone.removeClass('drop');
        dropZone.text("Загружено");
        window.location = "http://" + host_url + port_url + "/file/download?filename=" + filename;
        dropZone.text("Нейронные сети (обратное распространение ошибки)");
    };
    var error = function error(data) {
        $("#text_area").text("Произошла ошибка! " + data);
    }

});