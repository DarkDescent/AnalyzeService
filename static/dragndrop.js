/**
 * Created by a1 on 17.02.16.
 * скрипт отвечает за загрузку документов, которые переводятся мышкой в браузер (технология DragnDrop of files in browsers
 * основной код взят отсюда - https://habrahabr.ru/post/125424/
 */

$(document).ready(function() {
    var method_list = ["cluster", "cure", "classification", "neuron"];
    for (cur_method in method_list) {
        (function() {
            var dropZone = $('#dropZone_' + cur_method),
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
                fd.append('method', cur_method);
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
            };
            var error = function error(data) {
                $("#text_area").text("Произошла ошибка! " + data);
            }
        })();
    }

});