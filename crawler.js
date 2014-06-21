var request = require('request');
var async = require('async');
var	cheerio = require('cheerio');
var fs = require('fs');

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

var queryGoogle = function (query, page, cb){
	var url = googleUrl(query, page);
	request(url, function(error, response, body){
		if (error || response.statusCode !== 200)
      return cb(new Error('query fail: ' + url));

    parseGoogleResult(body, cb);
	});
};

var removeHash = function (url){
  return url.replace(/#.*$/, '');
};

var extractLinks = function(url, body, cb){
  var root = url.match(/^https?:\/\/[^\/]+/)[0] + '/';

  $ = cheerio.load(body);
  async.map($('a[href]').toArray(), function(item, cb){
    var href = $(item).attr('href');
    if (href.match(/^javascript/)) return cb();

    var url = removeHash(href);
    if (!url.match(/^http/)){
      url = root + url.replace(/^\//, '');
    }

    cb(null, url);
  }, cb);
};

var crawl = function (url, cb){
  if(!url) return cb();

  url = removeHash(url);
  if (crawled.indexOf(url) != -1) return cb();

  console.log('crawl url: ' + url);

  crawled.push(url);
  request(url, function (err, res, body){
    if(err || res.statusCode != 200) return cb();
    console.log('crawl url: ' + url + ' done');

    async.waterfall([
      function(cb){
        extractLinks(url, body, function(err, targetUrls){
          if(err) return cb(err);

          targetUrls = targetUrls.filter( function(url){
            if(!url) return false;

            return !url.match(/(jpg|png|gif|zip)$/i);
          });

          [].push.apply(urlList, targetUrls);

          cb(null, targetUrls);
        });
      }, 
      function(urls, cb){
        var item = {
          title: $(body).find('h1').first().text(),
          content: body.replace(/[\r\n\t]+/g, ' '),
          links: urls
        };

        var json = JSON.stringify(item);
        fs.appendFile('data/results.jl', json + '\n', cb);
      }
    ], cb);
  });
};

var crawled = []; // TODO append to files
var urlList = [];
var queryString = 'web development tutorial';
var totalLevel = 2;
var concurrent = 20;
var pages = 2;
var time = 5000;

process.argv.forEach(function(key, index, array) {
  var value = array[index + 1];
  switch(key){
    case '-p':
      pages = value;
      break;
    case '-t':
      time = parseInt(value, 10)*1000;
      break;
    case '-l':
      totalLevel = parseInt(value, 10);
      break;
  }
});

async.series([
  function (cb){
    async.timesSeries(pages, function (n, next){
      console.log('query google page: ' + n + '...');
      queryGoogle(queryString, n, next);
    }, function(err, results){
      if (err) return cb(err);
      var flatArr = [].concat.apply([], results);
      [].push.apply(urlList, flatArr.map(function (item){ return item.url; }));
      cb(null);
    });
  }, function (cb){
    async.timesSeries(totalLevel, function (level, next){
      console.log('level: ' + level + ', number of url: ' + urlList.length);

      var currentUrlList = urlList;
      urlList = [];

      async.eachLimit(currentUrlList, concurrent, crawl, next);
    }, cb);
  }
], function(err){
  console.log('done');
  console.log('total ' + crawled.length + ' pages crawled ');
});

