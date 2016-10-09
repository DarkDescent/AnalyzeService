/**
 * Created by DarkDescent on 09.02.16.
 * За основу работа по определению стиля русского языка - http://teneta.rinet.ru/hudlomer/article.html
 */

function wordCount(str) {
    var BG = new Array();

    var Guiraud = new Array();
    var fomenko = new Array();
    var Freq = new Array();
    var Zipf = new Array();
    var NZipf = new Array();
    var finvariant = 0;
    var hstr = 'на с за к по из у от для во без до о через со при про об ко над из-за из-под под и что но а да хотя когда чтобы если тоже или то есть зато будто не как же даже бы ли только вот то ни лишь ведь вон то-есть нибудь уже либо';

    var foma = hstr.split(/\s+/);
    for (var i = 0; i < foma.length; i++) {
        fomenko[foma[i]] = 1;
    }

    var wordLenHisto = new Array();
    var htextsize = str.length;
    str = prepStr(str);
    var tempArray = str.split(' ').sort();
    var count = 1;	// Iterate through all the words
    var wordlensum = 0;
    var wordlensumsq = 0;
    var totalwords = 0;
    var wlhMax = -1;
    for (var i = 0; i < tempArray.length; i++) {		// If an array element with the same name as
        var s = tempArray[i];
        var l = s.length;
        if (l < 30) {  // Unlikely word length
            if (l > 0) {
                wordlensum += l;
                wordlensumsq += l * l;
                totalwords++;
                if (fomenko[s]) {
                    finvariant++;
                }
            }
            if (Freq[s] > 0) {
                Freq[s]++;
            } else {
                Freq[s] = 1;
            }
            if (wordLenHisto[l]) {
                wordLenHisto[l]++;
            } else {
                wordLenHisto[l] = 1;
            }
            if (wordLenHisto[l] > wlhMax) {
                wlhMax = wordLenHisto[l];
            }
        }
    }


    if (totalwords > 0) {
        averl = wordlensum / totalwords;
        varl = wordlensumsq / totalwords - averl * averl;
        varlteor = 3.89 * averl - 10.67;
    } else {
        averl = 0;
        varl = 0;
        varlteor = 0;
    }

    var termcolor = '';

    AVERMIN = 3.89;


    if (averl < AVERMIN) {
        averl = AVERMIN
    }
    ;

    if (averl > 7.9) {
        averl = 7.9
    }
    ;

    hwidth = 100;

    hwidth = Math.floor(25 * (averl - AVERMIN));

    if (hwidth < 25){
        return "Разговорный стиль";
    }
    else if (hwidth < 50){
        return "Художественный стиль";
    }
    else if (hwidth < 75) {
        return "Газетная статья";
    }
    else {
        return "Научная статья";
    }
}

function prepStr(str) {
	str = str.toLowerCase();
	str = str.replace(/['"-]/g, "");
	//str = str.replace(/\W/g, " ");
   str = str.replace(/[^абвгдеёжзийклмнопрстуфхцчшщъыьэюя\-a-z]/g,' ');

	str = str.replace(/\s+/g, " ");
	return str;
}