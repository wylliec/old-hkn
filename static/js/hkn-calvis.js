/**
 * Copyright 2008 Google Inc.
 * 
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 * 
 *      http://www.apache.org/licenses/LICENSE-2.0
 * 
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

/**
 * @fileoverview This file contains the dynamic loader for CalVis.
 * @author api.austin@google.com (Austin Chau)
 */

// Namespace to protect this library from conflicting with external.
var calvis = {};

// URL paths of scripts to be loaded
calvis.baseUrl = '/static/js/';
calvis.coreUrl = calvis.baseUrl + 'hkn-calvis-core.js';

/**
 * This method loads all the dependent scripts for Calvis and invoke
 * the callback method when the loading is done.
 * @param {Function} callback The callback method that will be invoked when
 *   loading is completed.
 */  
calvis.ready = function(callback) {    // this is a normal loading
    calvis.fixIE();
    calvis.scriptLoad(calvis.coreUrl, callback);
};

/**
 * This method dynamically loads a script from an URL via script tag injection
 * @param {string} url The URL of the script to be loaded
 * @param {Function} callback The callback method that will be invoked when
 *   loading is completed.
 */ 
calvis.scriptLoad = function(url, callback) {

  //console.log('loading ' + url);
  var script = document.createElement('script');
  script.src = url;

  var heads = document.getElementsByTagName('head');

  if (heads.length > 0) {
    head = heads[0]; 
    head.appendChild(script);
  } else {
    head = document.createElement('head');    
    head.appendChild(script);
    document.body.parentNode.appendChild(head);
  }

  // most browsers
  script.onload = callback;  
  
  // IE 6 & 7
  script.onreadystatechange = function() {
    if (script.readyState == 'loaded' || script.readyState == 'complete') {
      callback();
      //console.log(url + ' is loaded, state= ' + script.readyState);
    }
  };

};

/**
 * This method fixes IE specific issues
 */ 
calvis.fixIE = function() {
  if (!Array.indexOf) {
    Array.prototype.indexOf = function(arg) {

      var index = -1;
      for (var i = 0; i < this.length; i++){
        var value = this[i];
        if (value == arg) {
          index = i;
          break;
        } 
      }
      return index;
    }
  }

  if (!window.console) {

    window.console = {};
    window.console.log = function(message) {
      var body = document.getElementsByTagName('body')[0];
      var messageDiv = document.createElement('div');
      messageDiv.innerHTML = message;
      body.insertBefore(messageDiv, body.lastChild);
    }
  } 

};
