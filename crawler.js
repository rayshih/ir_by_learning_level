var request = require('request'),
	cheerio = require('cheerio'),
	fs = require('fs'),
	moment = require('moment'),
	results = [], check = [], flag = [], query = [],
	pages = 2, index = 1, argc, errNum = 0, saved = 0, time = 5000;

process.argv.forEach(function(val, index, array) {
	if (val === '-p') pages = array[index+1];
	else if (val === '-t') time = parseInt(array[index+1])*1000;
	else {

	}
});


function req(i) {
	// console.log('page:'+i);
	var url = 'https://www.google.com.tw/search?q=web+development+tutorial&es_sm=91&ei=TI2iU6aJK4jMkwXp04FQ&start=' + (i*10).toString() + '&sa=N&biw=1015&bih=503';
	request(url, function (error, response, body) {
		if (error || response.statusCode !== 200) return;

		$ = cheerio.load(body);

		$('.g').each(function(iter, elem) {
			// purify the url
			var item = {"url":"","title":"","content":""};
			var str = $(this).find('.r a').attr('href'),
				res = str.replace("/url?q=", ""),
				title = $(this).find('h3').text();

			item.url = res.replace(/&sa=.*/gi, "");
			item.title = title;
			results.push(item);
		});

		//non-blocking
		if (check.length === pages-1) {
			for (var j = 0; j < results.length; j++)
				getContent(j);
		}
		else {
			check.push(true);
			setTimeout(function(){req(i+1)}, time);
		}
	});
}

function save(){
	saved = 1;
	var data = JSON.stringify(results, null, "\t");
	fs.writeFileSync('data/results.json', data);
}

function getContent(i){
	var url = results[i].url;

	request(url, function (error, response, body) {
		if (error || response.statusCode !== 200) {
			errNum++;
	    	return;
	  	}
		$ = cheerio.load(body);
		// results[i].content = $('body').text();
		results[i].content = $('body').text().replace(/[\r\t\n]/gi, "");

		//non-blocking
		if (flag.length === results.length-1 - errNum) {
			save();
		}
		else {
			flag.push(true);
		}
	});
}

setTimeout(function(){req(0)}, time);
