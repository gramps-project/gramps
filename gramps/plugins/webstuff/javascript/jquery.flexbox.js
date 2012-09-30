/*!
* jQuery FlexBox $Version: 0.9.6 $
*
* Copyright (c) 2008-2010 Noah Heldman and Fairway Technologies (http://www.fairwaytech.com/flexbox)
* Licensed under Ms-PL (http://www.codeplex.com/flexbox/license)
*
* $Date: 2010-11-24 01:02:00 PM $
* $Rev: 0.9.6.1 $
*/
(function($) {
    $.flexbox = function(div, o) {

        // TODO: in straight type-ahead mode (showResults: false), if noMatchingResults, dropdown appears after new match
        // TODO: consider having options.mode (select, which replaces html select; combobox; suggest; others?)
        // TODO: on resize (at least when wrapping within a table), the arrow is pushed down to the next line
        // TODO: check for boundary/value problems (such as minChars of -1) and alert them
        // TODO: add options for advanced paging template
        // TODO: general cleanup and refactoring, commenting
        // TODO: detailed Exception handling, logging
        // TODO: FF2, up arrow from bottom has erratic scroll behavior (if multiple flexboxes on page)
        // TODO: FF2 (and maybe IE7): if maxVisibleRows == number of returned rows, height is a bit off (maybe set to auto?)
        // TODO: escape key only works from input box (this might be okay)
        // TODO: make .getJSON parameters (object and callback function) configurable (e.g. when calling yahoo image search)
        // TODO: escape key reverts to previous value (FF only?) (is this a good thing?)

		// TEST: highlightMatches uses the case of whatever you typed in to replace the match string, which can look funny
        // TEST: handle pageDown and pageUp keys when scrolling through results
        // TEST: allow client-side paging (return all data initially, set paging:{pageSize:#}, and ensure maxCacheBytes is > 0)
        // TEST: accept json object as first parameter to flexbox instead of page source, and have it work like a combobox
        // TEST: implement no results template
        // TEST: implement noResultsText and class
        // TEST: watermark color should be configurable (and so should default input color)
        // TEST: exception handling and alerts for common mistakes
        // TEST: first example should use defaults ONLY
        // TEST: add property initialValue, so you can set it when the flexbox loads
        // TEST: handle hidden input value for form submissions
        // TEST: how can we allow programmatically setting the field value (and therefore hidden value).  add jquery function?
        // TEST: use pageSize parameter as threshold to switch from no paging to paging based on results
        // TEST: if you type in an input value that matches the html, it might display html code (try typing "class" in the input box)
        // TEST: don't require all paging subprops (let default override)
        // TEST: when tabbing from one ffb to another, the previous ffb results flash...
        // TEST: IE7: when two non-paging ffbs right after each other, with only a clear-both div between them, the bottom ffb jumps down when selecting a value, then jumps back up on mouseover
        // TEST: FF2, make sure we scroll to top before showing results (maxVisibleRows only)
        // TEST: if maxVisibleRows is hiding the value the user types in to the input, scroll to that value (is this even possible?)
        // TEST: make sure caching supports multiple ffbs uniquely
        // TEST: when entering a number in the paging input box, the results are displayed twice

        var timeout = false, 	// hold timeout ID for suggestion results to appear
        cache = [], 		    // simple array with cacheData key values, MRU is the first element
        cacheData = [],         // associative array holding actual cached data
        cacheSize = 0, 		    // size of cache in bytes (cache up to o.maxCacheBytes bytes)
        delim = '\u25CA',       // use an obscure unicode character (lozenge) as the cache key delimiter
        scrolling = false,
        pageSize = o.paging && o.paging.pageSize ? o.paging.pageSize : 0,
		retrievingRemoteData = false,
        $div = $(div).css('position', 'relative').css('z-index', 0);

        // The hiddenField MUST be appended to the div before the input, or IE7 does not shift the dropdown below the input field (it overlaps)
        var $hdn = $('<input type="hidden"/>')
            .attr('id', $div.attr('id') + '_hidden')
            .attr('name', $div.attr('id'))
            .val(o.initialId)
            .appendTo($div);
        var $input = $('<input/>')
            .attr('id', $div.attr('id') + '_input')
            .attr('autocomplete', 'off')
            .addClass(o.inputClass)
            .css('width', o.width + 'px')
            .appendTo($div)
            .click(function(e) {
                if (o.watermark !== '' && this.value === o.watermark)
                    this.value = '';
                else
                    this.select();
            })
            .focus(function(e) {
                $(this).removeClass('watermark');
            })
            .blur(function(e) {
				if (this.value === '') $hdn.val('');
                setTimeout(function() { if (!$input.data('active')) hideResults(); }, 200);
            })
            .keydown(processKeyDown);
        
        if (o.initialValue !== '')
            $input.val(o.initialValue).removeClass('watermark');
        else
            $input.val(o.watermark).addClass('watermark');

        var arrowWidth = 0;
        if (o.showArrow && o.showResults) {
            var arrowClick = function() {
                if ($ctr.is(':visible')) {
                    hideResults();
                }
                else {
                    $input.focus();
                    if (o.watermark !== '' && $input.val() === o.watermark)
                        $input.val('');
                    else
                        $input.select();
                    if (timeout)
                        clearTimeout(timeout);
                    timeout = setTimeout(function() { flexbox(1, true, o.arrowQuery); }, o.queryDelay);
                }
            };
            var $arrow = $('<span></span>')
                .attr('id', $div.attr('id') + '_arrow')
                .addClass(o.arrowClass)
                .addClass('out')
                .hover(function() {
                    $(this).removeClass('out').addClass('over');
                }, function() {
                    $(this).removeClass('over').addClass('out');
                })
                .mousedown(function() {
                    $(this).removeClass('over').addClass('active');
                })
                .mouseup(function() {
                    $(this).removeClass('active').addClass('over');
                })
                .click(arrowClick)
                .appendTo($div);
            arrowWidth = $arrow.width();
            $input.css('width', (o.width - arrowWidth) + 'px');
        }
        if (!o.allowInput) { o.selectFirstMatch = false; $input.click(arrowClick); } // simulate <select> behavior

        // Handle presence of CSS Universal Selector (*) that defines padding by verifying what the browser thinks the outerHeight is.
        // In FF, the outerHeight() will not pick up the correct input field padding
        var inputPad = $input.outerHeight() - $input.height() - 2;
        var inputWidth = $input.outerWidth() - 2;
        var top = $input.outerHeight();
		
        if (inputPad === 0) {
            inputWidth += 4;
            top += 4;
        }
        else if (inputPad !== 4) {
            inputWidth += inputPad;
            top += inputPad;
        }
		
        var $ctr = $('<div></div>')
            .attr('id', $div.attr('id') + '_ctr')
            .css('width', inputWidth + arrowWidth)
            .css('top', top)
            .css('left', 0)
            .addClass(o.containerClass)
            .appendTo($div)
			.mousedown(function(e) {
				$input.data('active', true);
			})
            .hide();

        var $content = $('<div></div>')
            .addClass(o.contentClass)
            .appendTo($ctr)
            .scroll(function() {
                scrolling = true;
            });

        var $paging = $('<div></div>').appendTo($ctr);
		$div.css('height', $input.outerHeight());

        function processKeyDown(e) {
            // handle modifiers
            var mod = 0;
            if (typeof (e.ctrlKey) !== 'undefined') {
                if (e.ctrlKey) mod |= 1;
                if (e.shiftKey) mod |= 2;
            } else {
                if (e.modifiers & Event.CONTROL_MASK) mod |= 1;
                if (e.modifiers & Event.SHIFT_MASK) mod |= 2;
            }
            // if the keyCode is one of the modifiers, bail out (we'll catch it on the next keypress)
            if (/16$|17$/.test(e.keyCode)) return; // 16 = Shift, 17 = Ctrl

            var tab = e.keyCode === 9, esc = e.keyCode === 27;
            var tabWithModifiers = e.keyCode === 9 && mod > 0;
            var backspace = e.keyCode === 8; // we will end up extending the delay time for backspaces...

            // tab is a special case, since we want to bubble events...
            if (tab) if (getCurr()) selectCurr();

            // handling up/down/escape/right arrow/left arrow requires results to be visible
            // handling enter requires that AND a result to be selected
            if ((/27$|38$|33$|34$/.test(e.keyCode) && $ctr.is(':visible')) ||
				(/13$|40$/.test(e.keyCode)) || !o.allowInput) {

                if (e.preventDefault) e.preventDefault();
                if (e.stopPropagation) e.stopPropagation();

                e.cancelBubble = true;
                e.returnValue = false;

                switch (e.keyCode) {
                    case 38: // up arrow
                        prevResult();
                        break;
                    case 40: // down arrow
                        if ($ctr.is(':visible')) nextResult();
                        else flexboxDelay(true);
                        break;
                    case 13: // enter
                        if (getCurr()) selectCurr();
                        else flexboxDelay(true);
                        break;
                    case 27: //	escape
                        hideResults();
                        break;
                    case 34: // page down
						if (!retrievingRemoteData) {
							if (o.paging) $('#' + $div.attr('id') + 'n').click();
							else nextPage();
						}
                        break;
                    case 33: // page up
						if (!retrievingRemoteData) {
							if (o.paging) $('#' + $div.attr('id') + 'p').click();
							else prevPage();
						}
                        break;
                    default:
                        if (!o.allowInput) { return; }
                }
            } else if (!esc && !tab && !tabWithModifiers) { // skip esc and tab key and any modifiers
                flexboxDelay(false, backspace);
            }
        }

        function flexboxDelay(simulateArrowClick, increaseDelay) {
            if (timeout) clearTimeout(timeout);
            var delay = increaseDelay ? o.queryDelay * 5 : o.queryDelay;
            timeout = setTimeout(function() { flexbox(1, simulateArrowClick, ''); }, delay);
        }

        function flexbox(p, arrowOrPagingClicked, prevQuery) {
            if (arrowOrPagingClicked) prevQuery = '';
            var q = prevQuery && prevQuery.length > 0 ? prevQuery : $.trim($input.val());

            if (q.length >= o.minChars || arrowOrPagingClicked) {
				// If we are getting data from the server, set the height of the content box so it doesn't shrink when navigating between pages, due to the $content.html('') below...
				if ($content.outerHeight() > 0)
					$content.css('height', $content.outerHeight());
                $content.html('').attr('scrollTop', 0);
				
                var cached = checkCache(q, p);
                if (cached) {
					$content.css('height', 'auto');
                    displayItems(cached.data, q);
                    showPaging(p, cached.t);
                }
                else {
                    var params = { q: q, p: p, s: pageSize, contentType: 'application/json; charset=utf-8' };
                    var callback = function(data, overrideQuery) {
                        if (overrideQuery === true) q = overrideQuery; // must compare to boolean because by default, the string value "success" is passed when the jQuery $.getJSON method's callback is called
                        var totalResults = parseInt(data[o.totalProperty]);

                        // Handle client-side paging, if any paging configuration options were specified
                        if (isNaN(totalResults) && o.paging) {
                            if (o.maxCacheBytes <= 0) alert('The "maxCacheBytes" configuration option must be greater\nthan zero when implementing client-side paging.');
                            totalResults = data[o.resultsProperty].length;

                            var pages = totalResults / pageSize;
                            if (totalResults % pageSize > 0) pages = parseInt(++pages);

                            for (var i = 1; i <= pages; i++) {
                                var pageData = {};
                                pageData[o.totalProperty] = totalResults;
                                pageData[o.resultsProperty] = data[o.resultsProperty].splice(0, pageSize);
                                if (i === 1) totalSize = displayItems(pageData, q);
                                updateCache(q, i, pageSize, totalResults, pageData, totalSize);
                            }
                        }
                        else {
                            var totalSize = displayItems(data, q);
                            updateCache(q, p, pageSize, totalResults, data, totalSize);
                        }
                        showPaging(p, totalResults);
						$content.css('height', 'auto');
						retrievingRemoteData = false;
                    };
					if (typeof (o.source) === 'object') {
						if (o.allowInput) callback(filter(o.source, params));
						else callback(o.source);
					}
					else {
						retrievingRemoteData = true;
						if (o.method.toUpperCase() == 'POST') $.post(o.source, params, callback, 'json');
						else $.getJSON(o.source, params, callback);
					}
                }
            } else
                hideResults();
        }
		
		function filter(data, params) {
			var filtered = {};
			filtered[o.resultsProperty] = [];
			filtered[o.totalProperty] = 0;
			var index = 0;
			
			for (var i=0; i < data[o.resultsProperty].length; i++) {
				var indexOfMatch = data[o.resultsProperty][i][o.displayValue].toLowerCase().indexOf(params.q.toLowerCase());
				if ((o.matchAny && indexOfMatch !== -1) || (!o.matchAny && indexOfMatch === 0)) {
					filtered[o.resultsProperty][index++] = data[o.resultsProperty][i];
					filtered[o.totalProperty] += 1;
				}
			}
			if (o.paging) {
				var start = (params.p - 1) * params.s;
				var howMany = (start + params.s) > filtered[o.totalProperty] ? filtered[o.totalProperty] - start : params.s;
				filtered[o.resultsProperty] = filtered[o.resultsProperty].splice(start, howMany);
			}
			return filtered;
		}

        function showPaging(p, totalResults) {
            $paging.html('').removeClass(o.paging.cssClass); // clear out for threshold scenarios
            if (o.showResults && o.paging && totalResults > pageSize) {
                var pages = totalResults / pageSize;
                if (totalResults % pageSize > 0) pages = parseInt(++pages);
                outputPagingLinks(pages, p, totalResults);
            }
        }

        function handleKeyPress(e, page, totalPages) {
            if (/^13$|^39$|^37$/.test(e.keyCode)) {
                if (e.preventDefault)
                    e.preventDefault();
                if (e.stopPropagation)
                    e.stopPropagation();

                e.cancelBubble = true;
                e.returnValue = false;

                switch (e.keyCode) {
                    case 13: // Enter
                        if (/^\d+$/.test(page) && page > 0 && page <= totalPages)
                            flexbox(page, true);
                        else
                            alert('Please enter a page number between 1 and ' + totalPages);
                        // TODO: make this alert a function call, and a customizable parameter
                        break;
                    case 39: // right arrow
                        $('#' + $div.attr('id') + 'n').click();
                        break;
                    case 37: // left arrow
                        $('#' + $div.attr('id') + 'p').click();
                        break;
                }
            }
        }

        function handlePagingClick(e) {
            flexbox(parseInt($(this).attr('page')), true, $input.attr('pq')); // pq == previous query
            return false;
        }

        function outputPagingLinks(totalPages, currentPage, totalResults) {
            // TODO: make these configurable images
            var first = '&lt;&lt;',
            prev = '&lt;',
            next = '&gt;',
            last = '&gt;&gt;',
            more = '...';

            $paging.addClass(o.paging.cssClass);

            // set up our base page link element
            var $link = $('<a/>')
                .attr('href', '#')
                .addClass('page')
                .click(handlePagingClick),
            $span = $('<span></span>').addClass('page'),
            divId = $div.attr('id');

            // show first page
            if (currentPage > 1) {
                $link.clone(true).attr('id', divId + 'f').attr('page', 1).html(first).appendTo($paging);
                $link.clone(true).attr('id', divId + 'p').attr('page', currentPage - 1).html(prev).appendTo($paging);
            }
            else {
                $span.clone(true).html(first).appendTo($paging);
                $span.clone(true).html(prev).appendTo($paging);
            }

            if (o.paging.style === 'links') {
                var maxPageLinks = o.paging.maxPageLinks;
                // show page numbers
                if (totalPages <= maxPageLinks) {
                    for (var i = 1; i <= totalPages; i++) {
                        if (i === currentPage) {
                            $span.clone(true).html(currentPage).appendTo($paging);
                        }
                        else {
                            $link.clone(true).attr('page', i).html(i).appendTo($paging);
                        }
                    }
                }
                else {
                    if ((currentPage + parseInt(maxPageLinks / 2)) > totalPages) {
                        startPage = totalPages - maxPageLinks + 1;
                    }
                    else {
                        startPage = currentPage - parseInt(maxPageLinks / 2);
                    }

                    if (startPage > 1) {
                        $link.clone(true).attr('page', startPage - 1).html(more).appendTo($paging);
                    }
                    else {
                        startPage = 1;
                    }

                    for (var i = startPage; i < startPage + maxPageLinks; i++) {
                        if (i === currentPage) {
                            $span.clone(true).html(i).appendTo($paging);
                        }
                        else {
                            $link.clone(true).attr('page', i).html(i).appendTo($paging);
                        }
                    }

                    if (totalPages > (startPage + maxPageLinks)) {
                        $link.clone(true).attr('page', i).html(more).appendTo($paging);
                    }
                }
            }
            else if (o.paging.style === 'input') {
                var $pagingBox = $('<input/>')
                    .addClass('box')
                    .click(function(e) {
                        this.select();
                    })
                    .keypress(function(e) {
                        return handleKeyPress(e, this.value, totalPages);
                    })
                    .val(currentPage)
                    .appendTo($paging);
            }

            if (currentPage < totalPages) {
                $link.clone(true).attr('id', divId + 'n').attr('page', +currentPage + 1).html(next).appendTo($paging);
                $link.clone(true).attr('id', divId + 'l').attr('page', totalPages).html(last).appendTo($paging);
            }
            else {
                $span.clone(true).html(next).appendTo($paging);
                $span.clone(true).html(last).appendTo($paging);
            }
            var startingResult = (currentPage - 1) * pageSize + 1;
            var endingResult = (startingResult > (totalResults - pageSize)) ? totalResults : startingResult + pageSize - 1;

            if (o.paging.showSummary) {
                var summaryData = {
                    "start": startingResult,
                    "end": endingResult,
                    "total": totalResults,
                    "page": currentPage,
                    "pages": totalPages
                };
                var html = o.paging.summaryTemplate.applyTemplate(summaryData);
                $('<br/>').appendTo($paging);
                $('<span></span>')
                    .addClass(o.paging.summaryClass)
                    .html(html)
                    .appendTo($paging);
            }
        }

        function checkCache(q, p) {
            var key = q + delim + p; // use null character as delimiter
            if (cacheData[key]) {
                for (var i = 0; i < cache.length; i++) { // TODO: is it possible to not loop here?
                    if (cache[i] === key) {
                        // pull out the matching element (splice), and add it to the beginning of the array (unshift)
                        cache.unshift(cache.splice(i, 1)[0]);
                        return cacheData[key];
                    }
                }
            }
            return false;
        }

        function updateCache(q, p, s, t, data, size) {
            if (o.maxCacheBytes > 0) {
                while (cache.length && (cacheSize + size > o.maxCacheBytes)) {
                    var cached = cache.pop();
                    cacheSize -= cached.size;
                }
                var key = q + delim + p; // use null character as delimiter
                cacheData[key] = {
                    q: q,
                    p: p,
                    s: s,
                    t: t,
                    size: size,
                    data: data
                }; // add the data to the cache at the hash key location
                cache.push(key); // add the key to the MRU list
                cacheSize += size;
            }
        }

        function displayItems(d, q) {
            var totalSize = 0, itemCount = 0;

            if (!d)
                return;
			
			$hdn.val($input.val());
            if (parseInt(d[o.totalProperty]) === 0 && o.noResultsText && o.noResultsText.length > 0) {
                $content.addClass(o.noResultsClass).html(o.noResultsText);
                $ctr.show();
                return;
            } else $content.removeClass(o.noResultsClass);

            for (var i = 0; i < d[o.resultsProperty].length; i++) {
                var data = d[o.resultsProperty][i],
                result = o.resultTemplate.applyTemplate(data),
                exactMatch = q === result,
                selectedMatch = false,
                hasHtmlTags = false,
				match = data[o.displayValue];

                if (!exactMatch && o.highlightMatches && q !== '') {
					var pattern = q,
					highlightStart = match.toLowerCase().indexOf(q.toLowerCase()),
                    replaceString = '<span class="' + o.matchClass + '">' + match.substr(highlightStart,q.length) + '</span>';
                    if (result.match('<(.|\n)*?>')) { // see if the content contains html tags
                        hasHtmlTags = true;
                        pattern = '(>)([^<]*?)(' + q + ')((.|\n)*?)(<)'; // TODO: look for a better way
                        replaceString = '$1$2<span class="' + o.matchClass + '">$3</span>$4$6';
                    }
                    result = result.replace(new RegExp(pattern.replace("[", "\\["), o.highlightMatchesRegExModifier), replaceString);
                }

                // write the value of the first match to the input box, and select the remainder,
                // but only if autoCompleteFirstMatch is set, and there are no html tags in the response
                if (o.autoCompleteFirstMatch && !hasHtmlTags && i === 0) {
                    if (q.length > 0 && match.toLowerCase().indexOf(q.toLowerCase()) === 0) {
                        $input.attr('pq', q); // pq == previous query
						$hdn.val(data[o.hiddenValue]);
                        $input.val(data[o.displayValue]);
                        selectedMatch = selectRange(q.length, $input.val().length);
                    }
                }

                if (!o.showResults) return;

                $row = $('<div></div>')
                    .attr('id', data[o.hiddenValue])
                    .attr('val', data[o.displayValue])
                    .addClass('row')
                    .html(result)
                    .appendTo($content);

                if (exactMatch || (++itemCount == 1 && o.selectFirstMatch) || selectedMatch) {
                    $row.addClass(o.selectClass);
                }
                totalSize += result.length;
            }

            if (totalSize === 0) {
                hideResults();
                return;
            }

            $ctr.parent().css('z-index', 11000);
            $ctr.show();

            $content
				.children('div')
				.mouseover(function() {
				    $content.children('div').removeClass(o.selectClass);
				    $(this).addClass(o.selectClass);
				})
				.mouseup(function(e) {
				    e.preventDefault();
				    e.stopPropagation();
				    selectCurr();
				});

            if (o.maxVisibleRows > 0) {
                var maxHeight = $row.outerHeight() * o.maxVisibleRows;
                $content.css('max-height', maxHeight);
            }
			
            return totalSize;
        }

        function selectRange(s, l) {
            var tb = $input[0];
            if (tb.createTextRange) {
                var r = tb.createTextRange();
                r.moveStart('character', s);
                r.moveEnd('character', l - tb.value.length);
                r.select();
            } else if (tb.setSelectionRange) {
                tb.setSelectionRange(s, l);
            }
            tb.focus();
            return true;
        }

        String.prototype.applyTemplate = function(d) {
            try {
                if (d === '') return this;
                return this.replace(/{([^{}]*)}/g,
                    function(a, b) {
                        var r;
                        if (b.indexOf('.') !== -1) { // handle dot notation in {}, such as {Thumbnail.Url}
                            var ary = b.split('.');
                            var obj = d;
                            for (var i = 0; i < ary.length; i++)
                                obj = obj[ary[i]];
                            r = obj;
                        }
                        else
                            r = d[b];
                        if (typeof r === 'string' || typeof r === 'number') return r; else throw (a);
                    }
                );
            } catch (ex) {
                alert('Invalid JSON property ' + ex + ' found when trying to apply resultTemplate or paging.summaryTemplate.\nPlease check your spelling and try again.');
            }
        };

        function hideResults() {
            $input.data('active', false); // for input blur
            $div.css('z-index', 0);
            $ctr.hide();
        }

        function getCurr() {
            if (!$ctr.is(':visible'))
                return false;

            var $curr = $content.children('div.' + o.selectClass);

            if (!$curr.length)
                $curr = false;

            return $curr;
        }

        function selectCurr() {
            $curr = getCurr();

            if ($curr) {
				$hdn.val($curr.attr('id'));
                $input.val($curr.attr('val')).focus();
                hideResults();

                if (o.onSelect) {
                    o.onSelect.apply($input[0]);
                }
            }
        }

        function supportsGetBoxObjectFor() {
            try {
                document.getBoxObjectFor(document.body);
                return true;
            }
            catch (e) {
                return false;
            }
        }

        function supportsGetBoundingClientRect() {
            try {
                document.body.getBoundingClientRect();
                return true;
            }
            catch (e) {
                return false;
            }
        }

        function nextPage() {
            $curr = getCurr();

            if ($curr && $curr.next().length > 0) {
                $curr.removeClass(o.selectClass);

                for (var i = 0; i < o.maxVisibleRows; i++) {
                    if ($curr.next().length > 0) {
                        $curr = $curr.next();
                    }
                }

                $curr.addClass(o.selectClass);
                var scrollPos = $content.attr('scrollTop');
                $content.attr('scrollTop', scrollPos + $content.height());
            }
            else if (!$curr)
                $content.children('div:first-child').addClass(o.selectClass);
        }

        function prevPage() {
            $curr = getCurr();

            if ($curr && $curr.prev().length > 0) {
                $curr.removeClass(o.selectClass);

                for (var i = 0; i < o.maxVisibleRows; i++) {
                    if ($curr.prev().length > 0) {
                        $curr = $curr.prev();
                    }
                }

                $curr.addClass(o.selectClass);
                var scrollPos = $content.attr('scrollTop');
                $content.attr('scrollTop', scrollPos - $content.height());
            }
            else if (!$curr)
                $content.children('div:last-child').addClass(o.selectClass);
        }

        function nextResult() {
            $curr = getCurr();

            if ($curr && $curr.next().length > 0) {
                $curr.removeClass(o.selectClass).next().addClass(o.selectClass);
                var scrollPos = $content.attr('scrollTop'),
                    curr = $curr[0], parentBottom, bottom, height;
                if (supportsGetBoxObjectFor()) {
                    parentBottom = document.getBoxObjectFor($content[0]).y + $content.attr('offsetHeight');
                    bottom = document.getBoxObjectFor(curr).y + $curr.attr('offsetHeight');
                    height = document.getBoxObjectFor(curr).height;
                }
                else if (supportsGetBoundingClientRect()) {
                    parentBottom = $content[0].getBoundingClientRect().bottom;
                    var rect = curr.getBoundingClientRect();
                    bottom = rect.bottom;
                    height = bottom - rect.top;
                }
                if (bottom >= parentBottom)
                    $content.attr('scrollTop', scrollPos + height);
            }
            else if (!$curr)
                $content.children('div:first-child').addClass(o.selectClass);
        }

        function prevResult() {
            $curr = getCurr();

            if ($curr && $curr.prev().length > 0) {
                $curr.removeClass(o.selectClass).prev().addClass(o.selectClass);
                var scrollPos = $content.attr('scrollTop'),
                curr = $curr[0],
                parent = $curr.parent()[0],
                parentTop, top, height;
                if (supportsGetBoxObjectFor()) {
                    height = document.getBoxObjectFor(curr).height;
                    parentTop = document.getBoxObjectFor($content[0]).y - (height * 2); // TODO: this is not working when i add another control...
                    top = document.getBoxObjectFor(curr).y - document.getBoxObjectFor($content[0]).y;
                }
                else if (supportsGetBoundingClientRect()) {
                    parentTop = parent.getBoundingClientRect().top;
                    var rect = curr.getBoundingClientRect();
                    top = rect.top;
                    height = rect.bottom - top;
                }
                if (top <= parentTop)
                    $content.attr('scrollTop', scrollPos - height);
            }
            else if (!$curr)
                $content.children('div:last-child').addClass(o.selectClass);
        }
    };

    $.fn.flexbox = function(source, options) {
        if (!source)
            return;

        try {
            var defaults = $.fn.flexbox.defaults;
            var o = $.extend({}, defaults, options);

            for (var prop in o) {
                if (defaults[prop] === undefined) throw ('Invalid option specified: ' + prop + '\nPlease check your spelling and try again.');
            }
            o.source = source;

            if (options) {
                o.paging = (options.paging || options.paging == null) ? $.extend({}, defaults.paging, options.paging) : false;

                for (var prop in o.paging) {
                    if (defaults.paging[prop] === undefined) throw ('Invalid option specified: ' + prop + '\nPlease check your spelling and try again.');
                }

                if (options.displayValue && !options.hiddenValue) {
                    o.hiddenValue = options.displayValue;
                }
            }

            this.each(function() {
                new $.flexbox(this, o);
            });

            return this;
        } catch (ex) {
            if (typeof ex === 'object') alert(ex.message); else alert(ex);
        }
    };

    // plugin defaults - added as a property on our plugin function so they can be set independently
    $.fn.flexbox.defaults = {
        method: 'GET', // One of 'GET' or 'POST'
        queryDelay: 100, // num of milliseconds before query is run.
        allowInput: true, // set to false to disallow the user from typing in queries
        containerClass: 'ffb',
        contentClass: 'content',
        selectClass: 'ffb-sel',
        inputClass: 'ffb-input',
        arrowClass: 'ffb-arrow',
        matchClass: 'ffb-match',
        noResultsText: 'No matching results', // text to show when no results match the query
        noResultsClass: 'ffb-no-results', // class to apply to noResultsText
        showResults: true, // whether to show results at all, or just typeahead
        selectFirstMatch: true, // whether to highlight the first matching value
        autoCompleteFirstMatch: false, // whether to complete the first matching value in the input box
        highlightMatches: true, // whether all matches within the string should be highlighted with matchClass
        highlightMatchesRegExModifier: 'i', // 'i' for case-insensitive, 'g' for global (all occurrences), or combine
		matchAny: true, // for client-side filtering ONLY, match any occurrence of the search term in the result (e.g. "ar" would find "area" and "cart")
        minChars: 1, // the minimum number of characters the user must enter before a search is executed
        showArrow: true, // set to false to simulate google suggest
        arrowQuery: '', // the query to run when the arrow is clicked
        onSelect: false, // function to run when a result is selected
        maxCacheBytes: 32768, // in bytes, 0 means caching is disabled
        resultTemplate: '{name}', // html template for each row (put json properties in curly braces)
        displayValue: 'name', // json element whose value is displayed on select
        hiddenValue: 'id', // json element whose value is submitted when form is submitted
        initialValue: '', // what should the value of the input field be when the form is loaded?
        initialId: '', // what should the value of the hidden field be when the form is loaded?
        watermark: '', // text that appears when flexbox is loaded, if no initialValue is specified.  style with css class '.ffb-input.watermark'
        width: 200, // total width of flexbox.  auto-adjusts based on showArrow value
        resultsProperty: 'results', // json property in response that references array of results
        totalProperty: 'total', // json property in response that references the total results (for paging)
        maxVisibleRows: 0, // default is 0, which means it is ignored.  use either this, or paging.pageSize
        paging: {
            style: 'input', // or 'links'
            cssClass: 'paging', // prefix with containerClass (e.g. .ffb .paging)
            pageSize: 10, // acts as a threshold.  if <= pageSize results, paging doesn't appear
            maxPageLinks: 5, // used only if style is 'links'
            showSummary: true, // whether to show 'displaying 1-10 of 200 results' text
            summaryClass: 'summary', // class for 'displaying 1-10 of 200 results', prefix with containerClass
            summaryTemplate: 'Displaying {start}-{end} of {total} results' // can use {page} and {pages} as well
        }
    };

    $.fn.setValue = function(val) {
        var id = '#' + this.attr('id');
        $(id + '_hidden,' + id + '_input').val(val).removeClass('watermark');
    };
})(jQuery);