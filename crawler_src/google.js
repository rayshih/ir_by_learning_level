var request = require('request');
var	cheerio = require('cheerio');

var googleUrl = function(query, page){
  var queryString = query.replace(/\s+/g, '+');
  var start = page * 10;
  return 'https://www.google.com.tw/search?q=' + queryString + '&start=' + start;
};

var parseGoogleResult = function (body, cb){
  $ = cheerio.load(body);
  var items = $('.g').map(function (iter, elem){
    var rawUrl = $(this).find('.r a').attr('href');

    return {
      url : rawUrl.replace("/url?q=", "").replace(/&sa=.*/gi, ""),
      title : $(this).find('h3').text()
    };
  }).toArray();

  cb(null, items);
};

module.exports = function (query, page, cb){
	var url = googleUrl(query, page);
	request(url, function(error, response, body){
		if (error || response.statusCode !== 200)
      return cb(new Error('query fail: ' + url));

    parseGoogleResult(body, cb);
	});
};
