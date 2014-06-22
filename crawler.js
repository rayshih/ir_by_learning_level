var request = require('request');
var async = require('async');
var fs = require('fs');
var google = require('./crawler_src/google');
var utils = require('./crawler_src/utils');

var queryString = 'web development tutorial';
var currentLevel = 0;
var totalLevel = 3;
var concurrent = 20;
var pages = 2;

var crawled = [];
var urlList = [];

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

var crawl = function (url, cb){
  if(!url) return cb();

  url = utils.removeHash(url);
  if (crawled.indexOf(url) != -1) return cb();

  console.log('crawl url: ' + url);

  async.waterfall([
    function (cb) {
      crawled.push(url);
      cb();
    },
    function (cb) {
      request(url, function (err, res, body){
        if (err) return cb(err);
        console.log('crawl url: ' + url + ' status: ' + res.statusCode);

        if(res.statusCode != 200) return cb(new Error('request fail'));

        cb(null, body);
      });
    },
    function (body, cb) {
      utils.extractLinks(url, body, function(err, targetUrls){
        if(err) return cb(err);

        targetUrls = targetUrls.filter( function(url){
          if(!url) return false;

          return !url.match(/(jpg|png|gif|zip|js)$/i);
        });

        async.each(targetUrls, function(url, cb){
          if (crawled.indexOf(url) != -1) return cb();

          urlList.push(url);
          utils.appendListFile('tmp/crawl_urls_' + (currentLevel + 1), url, cb);
        }, function(err){
          if (err) return cb(err);
          cb(null, body, targetUrls);
        });
      });
    },
    function (body, urls, cb) {
      var item = {
        url: url,
        title: $(body).find('h1').first().text(),
        content: body.replace(/[\r\n\t]+/g, ' '),
        links: urls
      };

      var json = JSON.stringify(item);
      utils.appendListFile('data/results.jl', json, cb);
    },
    function (cb) {
      console.log('crawl url: ' + url + ' done');
      utils.appendListFile('tmp/crawl_crawled_urls', url, cb);
    }
  ], function(err){
    if (err) {
      console.log('crawl url: ' + url + ' fail, err = ' + err);
    }

    cb(); // ignore err
  });
};

var levelZeroCrawlFromGoogle = function(cb){
  async.waterfall([
    function (cb) {
      fs.unlink('tmp/crawl_urls_' + (currentLevel + 1), function () {
        cb();
      });
    },
    function (cb) {
      async.timesSeries(pages, function (n, next){
        console.log('query google page: ' + n + '...');
        google(queryString, n, next);
      }, cb);
    },
    function (results, cb) {
      urlList = [];
      var flatArr = [].concat.apply([], results);
      async.each(flatArr, function (item, cb){
        url = item.url;
        urlList.push(url);
        utils.appendListFile('tmp/crawl_urls_' + (currentLevel + 1), url, cb);
      }, cb);
    },
    function(cb){
      fs.writeFile('tmp/crawl_finished_level', currentLevel + 1, cb);
    }
  ], function (err) {
    currentLevel++;
    cb();
  });
};

var crawlByLevel = function (cb) {
  async.whilst(function () {
    return totalLevel > currentLevel;
  }, function (cb){
    console.log('level: ' + currentLevel + ', number of url: ' + urlList.length);

    var currentUrlList = urlList;
    urlList = [];

    async.series([
      function (cb) {
        fs.unlink('tmp/crawl_urls_' + (currentLevel + 1), function () {
          cb();
        });
      },
      function(cb){
        async.eachLimit(currentUrlList, concurrent, crawl, cb);
      },
      function(cb){
        fs.writeFile('tmp/crawl_finished_level', currentLevel + 1, cb);
      },
      function (cb) {
        currentLevel++;
        cb();
      }
    ], cb);
  }, cb);
};

async.series([
  function(cb){
    fs.readFile('tmp/crawl_finished_level', function (err, data) {
      var currentLevel = parseInt(data, 10) || 0;
      cb(null, currentLevel);
    });
  },
  function (cb) {
    utils.loadListFile('tmp/crawl_crawled_urls', cb);
  }
], function(err, results){
  currentLevel = results[0];
  crawled = results[1] || [];

  var execFlow = [];
  if (currentLevel === 0) {
    execFlow.push(levelZeroCrawlFromGoogle);
  } else {
    execFlow.push(function (cb) {
      utils.loadListFile('tmp/crawl_urls_' + currentLevel, function (err, list) {
        urlList = list;
        cb();
      });
    });
  }

  execFlow.push(crawlByLevel);

  async.series(execFlow, function(err){
    console.log('done');
    console.log('total ' + crawled.length + ' pages crawled ');
  });
});

