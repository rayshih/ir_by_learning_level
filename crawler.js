var request = require('request'),
	cheerio = require('cheerio'),
	fs = require('fs'),
	moment = require('moment'),
	results = [], check = [],
	pages = 2, index = 1, test = [];


var flag = [];
for (var i = 0; i < pages; i++) flag.push(false);
function req(i) {
	var url = 'https://www.google.com.tw/search?q=web+development+tutorial&es_sm=91&ei=TI2iU6aJK4jMkwXp04FQ&start=' + (i*10).toString() + '&sa=N&biw=1015&bih=503';
	request(url, function (error, response, body) {
		if (error || response.statusCode !== 200) {
	    	return;
	  	}
		$ = cheerio.load(body);

		$('.g').each(function(iter, elem) {
			// purify the url
			var item = {"url":""};
			var regex=/&sa=.*/gi;
			str = $(this).find('.r a').attr('href');
			res = str.replace("/url?q=", "");

			item.url = res.replace(regex, "");
			results.push(item);

			// results.splice(-1, 0, item);
			// console.log(results);

			// var n = JSON.parse(JSON.stringify(news));
			// for (var j = 0; j < categories.length; j++) {
			// 	if ($(this).find('h2').text() === categories[j]) {
			// 		data[j].news_count++;
			// 		n.title = $(this).find('h1').text();
			// 		n.url = $(this).find('a').attr('href');
			// 		n.time = $(this).find('time').text();
			// 		n.video = $(this).hasClass('hsv');
			// 		data[j].news.push(n);
			// 		flag[i] = true;
			// 		break;
			// 	}
			// }
		});
		if (check.length === pages-1) 
			save();
		else 
			check.push(true);
	});
}

function save(){
	var data = JSON.stringify(results, null, "\t");
	fs.writeFileSync('results.json', data);
}

for (var i = 0; i < pages; i++) {
	req(i);
}