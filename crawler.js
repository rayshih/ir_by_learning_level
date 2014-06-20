var request = require('request'),
	cheerio = require('cheerio'),
	fs = require('fs'),
	moment = require('moment');

var results = [], check = [],
	pages = 2, index = 1, test = [];

var flag = [];
for (var i = 0; i < pages; i++) flag.push(false);

function req(i) {
	var url = 'https://www.google.com.tw/search?q=web+development+tutorial&es_sm=91&ei=TI2iU6aJK4jMkwXp04FQ&start=' + (i*10).toString() + '&sa=N&biw=1015&bih=503';
	request(url, function (error, response, body) {
		if (error || response.statusCode !== 200) return;

		$ = cheerio.load(body);

		$('.g').each(function(iter, elem) {
			// purify the url
			var item = [];
			var regex=/&sa=.*/gi;
			var str = $(this).find('.r a').attr('href'),
				res = str.replace("/url?q=", ""),
				title = $(this).find('h3').text();

			item.url = res.replace(regex, "");
			item.title = title;
			results.push(item);
		});

		if (check.length === pages-1)
			save();
		else
			check.push(true);
	});
}

function save(){
	var data = JSON.stringify(results, null, "\t");
	fs.writeFileSync('data/results.json', data);
}

for (var i = 0; i < pages; i++) {
	req(i);
}
