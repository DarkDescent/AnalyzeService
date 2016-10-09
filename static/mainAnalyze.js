/**
 * Created by DarkDescent on 04.02.2016.
 */

isShow = false;

function analyzethat()
{
    atext = $("#text_area").text();
    if (atext == ""){
        $("#text_area").text("Вы не ввели текст!");
        return;
    }

    var urls = [
        "/analyze/basic",
        "/analyze/cognate",
        "/analyze/orpho",
        "/analyze/annotate",
        "/analyze/parser"
    ];

    $("a.button").attr("title", "Обработка...");
    $("a.button").text("Обработка...");
    $("a.button").attr("disable", true);

    $.ajax({
        url: urls[0],
        data: {
            text: atext
        },
        success: answerBasic,
        error: error,
        method: "POST"
    });

    $.ajax({
       url: urls[1],
       data: {
            text: atext
       },
       success: answerCognate,
       error: error,
       method: "POST"
    });

    $.ajax({
       url: urls[2],
       data: {
            text: atext
       },
       success: answerOrpho,
       error: error,
       method: "POST"
    });

    $.ajax({
       url: urls[3],
       data: {
            text: atext
       },
       success: answerAnnotate,
       error: error,
       method: "POST"
    });

    $.ajax({
       url: urls[4],
       data: {
            text: atext
       },
       success: answerParser,
       error: error,
       method: "POST"
    });
}

function changeRatio(value){
    $("#range-ratio-envelope").text(value);
}

function askStatus(){
    while (true) {
        $.ajax({
            url: "/queue",
            data: {
                type: "status"
            },
            success: function (data) {

            },
            error: error,
            method: "POST"
        });
    }
}

function putQueue(text, name, ratio, is_pref)
{
    atext = text;
    aname = name;
    accur = ratio;
    if (atext == ""){
        $("#text_area").text("Вы не ввели текст!");
        return;
    }
    $("a.button").attr("title", "Обработка...");
    $("a.button").text("Обработка...");
    $("a.button").attr("disable", true);
    $.ajax({
       url: "http://" + host_url + port_url + "/queue",
       data: {
            text: atext,
            name: aname,
            type: "enqueue",
            accuracy: accur,
            is_prefix: is_pref
       },
       success: answerQueue,
       error: error,
       method: "POST"
    });
}

isShowArchive = [];
isShowResultsTable = false;



$(document).ready(function(){
    var ws = new WebSocket("ws://" + host_url + port_url + "/websocket");

    ws.onopen = function(){
        setInterval(function(){ ws.send("status")}, 2000);
    };

    ws.onmessage = function(evt){
        if(evt.data == "None"){
            $("#jobs_descr").text("Задачи: (пусто)");
            $("#jobs_status").html("");
        }
        else {
            var temp1 = "$('div #results_table').toggle(); isShowResultsTable = ~ isShowResultsTable;";
            var temp2 = "document.getElementById('clear_form').style.display='block';document.getElementById('fade').style.display='block'";
            var tasks_html = 'Задачи <a href="javascript:" style="text-decoration: none" onclick="'+ temp1 + '">(показать)</a> <a href="javascript:" style="text-decoration: none" onclick="'+ temp2 + '">(очистить)</a>';
            $("#jobs_descr").html(tasks_html);
            results = JSON.parse(evt.data);
            if (!isShowResultsTable)
                var result_text = '<div id="results_table" style="display: none; margin-left: 10px;">';
            else
                var result_text = '<div id="results_table" style="display: block; margin-left: 10px;">';
            for (var key in results) {
                if (results.hasOwnProperty(key)) {
                    var temp_result = results[key];
                    if (temp_result[0]["archive"] == "") {
                        for (var j = (temp_result.length - 1); j >= 0; j--) {
                            var result = temp_result[j];
                            if (result["status"] == "queued")
                                result_text += "Задача " + result["name"] + ': <span style="color: #ffdc34">находится в очереди</span><br>';
                            else if (result["status"] == "failed")
                                result_text += "Задача " + result["name"] + ': <span style="color: red">провалена</span><br>';
                            else if (result["status"] == "finished") {
                                var on_click = "processSocketResult('" + result["id"] + "');";
                                if ((j == (temp_result.length - 1) && (isShow))) {
                                    processSocketResult(result["id"]);
                                    isShow = false;
                                }
                                result_text += 'Задача ' + '<a href="javascript:;" style="text-decoration: none" onclick="' + on_click + '">' + result["name"] + ' </a>: <span style="color: green">завершена</span><br>';
                            }
                            else if (result["status"] == "started")
                                result_text += "Задача " + result["name"] + ': <span style="color: #ffdc34">находится в очереди</span><br>';
                            else if (result["status"] == "deleted")
                                result_text += "Задача " + result["name"] + ': <span>удалена</span><br>';
                            else
                                result_text += '<span style="color: red">Произошла ошибка, обратитесь к администратору</span><br>';


                        }
                    }
                    else {
                        if (!isShowArchive.hasOwnProperty(key))
                            isShowArchive[key] = false;
                        var on_show = "$('div .archive_" + key + "').toggle(); isShowArchive['" + key + "'] = ~ isShowArchive['" + key + "'];";
                        result_text += 'Задача ' + '<a href="javascript:;" style="text-decoration: none" onclick="' + on_show + '">' + temp_result[0]["archive"] + '</a> (архив)<br>';
                        if (isShowArchive[key]) {
                            result_text += '<div style="margin-left: 10px; display: block" class="archive_' + key + '">';
                        }
                        else {
                            result_text += '<div style="margin-left: 10px; display: none" class="archive_' + key + '">';
                        }
                        for (j = (temp_result.length - 1); j >= 0; j--) {
                            var result = temp_result[j];
                            if (result["status"] == "queued")
                                result_text += result["name"] + ': <span style="color: #ffdc34">находится в очереди</span><br>';
                            else if (result["status"] == "failed")
                                result_text += result["name"] + ': <span style="color: red">провалена</span><br>';
                            else if (result["status"] == "finished") {
                                var on_click = "processSocketResult('" + result["id"] + "');";
                                result_text += '<a href="javascript:;" style="text-decoration: none" onclick="' + on_click + '">' + result["name"] + ' </a>: <span style="color: green">завершена</span><br>';
                            }
                            else if (result["status"] == "started")
                                result_text += result["name"] + ': <span style="color: #ffdc34">находится в очереди</span><br>';
                            else if (result["status"] == "deleted")
                                result_text += result["name"] + ': <span>удалена</span><br>';
                            else
                                result_text += '<span style="color: red">Произошла ошибка, обратитесь к администратору</span><br>';
                        }
                        result_text += '</div>';
                    }
                }
            }
            result_text += '</div>';
            $("#jobs_status").html(result_text);
        }
    };
    ws.onclose = function(){
        $("#jobs_descr").text("Задачи: (соединение закрыто)");
    };
});

var answerQueue = function answerQueue(data) {
    $("a.button").attr("title", "Анализируется");
    $("a.button").attr("disable", false);
    if (data["status"] == "started"){
        $("a.button").text("Отправить на анализ");


    }
    else if(data["status"] == "failed") {
        $("a.button").text("Задачу не удалось запустить");
    }
}

function processSocketResult(name){
    $.get(
        "http://" + host_url + port_url + "/job/job_take",
        {
            job_id: name
        },
        onSocketSuccess
    );
}

function ClearJobs(){

    $.get(
        "http://" + host_url + port_url + "/job/job_clear",
        "http://" + host_url + port_url + "/job/job_clear",
        onClearSuccess
    );
}

function onSocketSuccess(data){
    var dataParsed = JSON.parse(data);
    if (dataParsed["basic"]["langShort"] == "ru"){
        var textStyle = wordCount(dataParsed["text"]);
        $("#style").text(textStyle);
    }
    // $("#text_area").text(dataParsed["text"]);
    answerBasic(dataParsed["basic"]);
    answerCognate(dataParsed["cognate"]);
    answerAnnotate(dataParsed["annotate"]);
    answerOrpho(dataParsed["orpho"]);
    answerParser(dataParsed["parser"]);
}

function onClearSuccess(data){

}

var answerBasic = function answerBasic(data){
    $("#lang").text(data["lang"]);
    // информация по показателю закона Ципфа
    if (parseFloat(data["zipfSimple"]) > 90) {
        var zipfHTML = '<span style="color: green">' + data["zipfSimple"] + '% (хорошо)</span>';
    }
    else if (parseFloat(data["zipfSimple"]) > 6) {
        var zipfHTML = '<span style="color: #E5C01F">' + data["zipfSimple"] + '% (удовлетворительно)</span>';
    }
    else {
        var zipfHTML = '<span style="color: red">' + data["zipfSimple"] + '% (плохо) </span>';
    }
    $("#zipf").html(zipfHTML);

    // информация по показателю водности
    if (parseFloat(data["water"]) < 10) {
        var waterHTML = '<span style="color: green">' + data["water"] + '% (хорошо) </span>';
    }
    else if (parseFloat(data["water"]) < 30) {
        var waterHTML = '<span style="color: yellowgreen">' + data["water"] + '% (оптимально) </span>';
    }
    if (parseFloat(data["water"]) < 60) {
        var waterHTML = '<span style="color: #E5C01F">' + data["water"] + '% (удовлетворительно) </span>';
    }
    else {
        var waterHTML = '<span style="color: red">' + data["water"] + '% (плохо) </span>';
    }
    $("#water").html(waterHTML);

    // информация по показателю тошноты
    if (parseFloat(data["nausea"]) < 3) {
        var nauseaHTML = '<span style="color: green">' + data["nausea"] + '% (хорошо) </span>';
    }
    else if (parseFloat(data["nausea"]) < 4) {
        var nauseaHTML = '<span style="color: yellowgreen">' + data["nausea"] + '% (оптимально) </span>';
    }
    else if (parseFloat(data["nausea"]) < 7) {
        var nauseaHTML = '<span style="color: #E5C01F">' + data["nausea"] + '% (удовлетворительно) </span>';
    }
    else {
        var nauseaHTML = '<span style="color: red">' + data["nausea"] + '% (плохо) </span>';
    }
    $("#nausea").html(nauseaHTML);

    // информация по показателю читабельности Flesch-Kincaid
    if (parseFloat(data["readability"]["kincaid"]) < 20){
        var fleschHTML = '<span style="color: red">' + data["readability"]["kincaid"] + ' (тяжело) </span>';
    }
    else if (parseFloat(data["readability"]["kincaid"]) < 60){
        var fleschHTML = '<span style="color: #E5C01F">' + data["readability"]["kincaid"] + ' (немного трудно) </span>';
    }
    else if (parseFloat(data["readability"]["kincaid"]) < 90){
        var fleschHTML = '<span style="color: yellowgreen">' + data["readability"]["kincaid"] + ' (просто) </span>';
    }
    else{
        var fleschHTML = '<span style="color: green">' + data["readability"]["kincaid"] + ' (очень легко) </span>';
    }
    $("#flesch").html(fleschHTML);

    // информация по показателю читабельности Liau
    if (parseFloat(data["readability"]["liau"]) < 6){
        var liauHTML = '<span style="color: green">' + data["readability"]["liau"] + ' (легко) </span>';
    }
    else if (parseFloat(data["readability"]["liau"]) < 12){
        var liauHTML = '<span style="color: #E5C01F">' + data["readability"]["liau"] + ' (средне) </span>';
    }
    else {
        var liauHTML = '<span style="color: red">' + data["readability"]["liau"] + ' (тяжело) </span>';
    }
    $("#liau").html(liauHTML);

    // информация по показателю читабельности Smog
    if (parseFloat(data["readability"]["smog"]) < 8){
        var smogHTML = '<span style="color: green">' + data["readability"]["smog"] + ' (легко) </span>';
    }
    else if (parseFloat(data["readability"]["smog"]) < 14){
        var smogHTML = '<span style="color: #E5C01F">' + data["readability"]["smog"] + ' (средне) </span>';
    }
    else {
        var smogHTML = '<span style="color: red">' + data["readability"]["smog"] + ' (тяжело) </span>';
    }
    $("#smog").html(smogHTML);

    // информация по показателю читабельности ARI
    if (parseFloat(data["readability"]["ari"]) < 7){
        var ariHTML = '<span style="color: green">' + data["readability"]["ari"] + ' (легко) </span>';
    }
    else if (parseFloat(data["readability"]["ari"]) < 12){
        var ariHTML = '<span style="color: #E5C01F">' + data["readability"]["ari"] + ' (средне) </span>';
    }
    else {
        var ariHTML = '<span style="color: red">' + data["readability"]["ari"] + ' (тяжело) </span>';
    }
    $("#ari").html(ariHTML);


    var freqwHTML = "";
    var freqwsHTML = "";

    //$("#freqw").text(answer["freqWords"]);
    // каждый элемент внутри параметра freqWords представляет собой список, в котором первый элемент - слово, второй - сколько оно раз встречалось
    data["freqWords"].forEach(function(item, i){
       freqwHTML = freqwHTML + item[0] + " - " + item[1] + "<br>";
    });
    $("#freqw").html(freqwHTML);

    //$("#freqsw").text(answer["freqStopWords"]);
    // каждый элемент внутри параметра freqWords представляет собой список, в котором первый элемент - слово, второй - сколько оно раз встречалось
    data["freqStopWords"].forEach(function(item, i){
       freqwsHTML = freqwsHTML + item[0] + " - " + item[1] + "<br>";
    });
    $("#freqsw").html(freqwsHTML);
}

var answerCognate = function answerCognate(data) {
    /*$("a.button").attr("title", "Отправить на анализ");
    $("a.button").text("Отправить на анализ");
    $("a.button").attr("disable", false);*/
    $("#content2 .result").html(data);
}

var answerOrpho = function answerOrpho(data) {
    /*$("a.button").attr("title", "Отправить на анализ");
    $("a.button").text("Отправить на анализ");
    $("a.button").attr("disable", false);*/
    $("#content3 .result").html(data);
}

var answerAnnotate = function answerAnnotate(data){
    /*$("a.button").attr("title", "Отправить на анализ");
    $("a.button").text("Отправить на анализ");
    $("a.button").attr("disable", false);*/
    lsa_annotate = data["lsa"];
    edm_annotate = data["edmundson"];
    kl_annotate = data["klsum"];
    lex_annotate = data["lexrank"];
    luhn_annonate = data["luhn"];
    sum_annotate = data["sumbasic"];
    text_annotate = data["textrank"];
    $("#content4 .result").text(edm_annotate);
}

var answerParser= function answerParser(data){
    /*$("a.button").attr("title", "Отправить на анализ");
    $("a.button").text("Отправить на анализ");
    $("a.button").attr("disable", false);*/
    var quality_html = "";
    $("#content5 .result").html(data["text"]);
    if (data["quality"] == "good")
        quality_html = '<span style="font-color:green">Хорошо</span>';
    else
        quality_html = '<span style="font-color:red">Плохо</span>';
    $("#quality_p").html(quality_html);
}

var error = function error(xhr, ajaxOptions, thrownError){
    $("#text_area").text("Произошла ошибка!");
}

function changeAnnotateAlgorithm (algorithm){
    var algorithmList = {
        "lsa": "Latent Semantic Analysis",
        "edmundson": "Edmundson",
        "klsum": "KL-Sum",
        "lexrank": "LexRank",
        "luhn": "Luhn",
        "sumbasic": "SumBasic",
        "textrank": "TextRank"
    };

    if (!(algorithm in algorithmList)) {
        return;
    }
    else {
        $("#algorithm_name").text(algorithmList[algorithm]);
    }
    switch (algorithm) {
        case "lsa":
            $("#content4 .result").text(lsa_annotate);
            break;
        case "edmundson":
            $("#content4 .result").text(edm_annotate);
            break;
        case "klsum":
            $("#content4 .result").text(kl_annotate);
            break;
        case "lexrank":
            $("#content4 .result").text(lex_annotate);
            break;
        case "luhn":
            $("#content4 .result").text(luhn_annotate);
            break;
        case "sumbasic":
            $("#content4 .result").text(sum_annotate);
            break;
        case "textrank":
            $("#content4 .result").text(text_annotate);
            break;
        default:
            return;
    }


}


function prepareDate(date_info){
    var hours = date_info.getHours();
    if (hours < 10)
        hours = '0' + hours.toString();
    var minutes = date_info.getMinutes();
    if (minutes < 10)
        minutes = '0' + minutes.toString();
    var seconds = date_info.getSeconds();
    if (seconds < 10)
        seconds = '0' + seconds.toString();
    var day = date_info.getDay();
    if (day < 10)
        day = '0' + day.toString();
    var month = date_info.getMonth();
    if (month < 10)
        month = '0' + month.toString();
    var year = date_info.getFullYear();
    return hours + ':' + minutes + ':' + seconds + '. ' + day + '.' + month + '.' + year + '.';
}
function sendQuery() {
    var text = $("#text_area").text();
    // var name = $("#your-name").val();
    // var rat = $("#range-input-envelope").val()
    // if ((text != "") && (name != "")) {
    isShow = true;
    if (text != "") {
        // document.getElementById('envelope').style.display = 'none';
        // document.getElementById('fade').style.display = 'none';
        // $(".title").text("Введите название задачи");
        var name = prepareDate(new Date());
        var rat = $("#range-input-envelope").val();
        if ($("#prefix_check").prop("checked"))
            var prefix_check = 0;
        else
            var prefix_check = 1;
        putQueue(text, name, rat, prefix_check);
    }
    /*else {
        $(".title").text("Вы не ввели текст!");
    }*/
}