(function () {
    'use strict';

    var isMac = /Mac/i.test(navigator.userAgent);
    window.onload = function () {
        require(['vs/editor/editor.main'], function () {
            var loading = document.getElementById('loading');
            loading.parentNode.removeChild(loading);
            load();
        });
    };

    var editor = null;
    var output = null;

    var sourceModel = null;
    var outputModel = null;

    globalThis.pyodideWorker = null;

    var id = 0;

    function load() {
        initPyodide();
        function layout() {
            var GLOBAL_PADDING = 20;

            var WIDTH = window.innerWidth - 2 * GLOBAL_PADDING;
            var HEIGHT = window.innerHeight;

            var TITLE_HEIGHT = 110;
            var FOOTER_HEIGHT = 80;
            var TABS_HEIGHT = 20;
            var INNER_PADDING = 20;
            var SWITCHER_HEIGHT = 30;

            var HALF_WIDTH = Math.floor((WIDTH - INNER_PADDING) / 2);
            var REMAINING_HEIGHT = HEIGHT - TITLE_HEIGHT - FOOTER_HEIGHT - SWITCHER_HEIGHT;

            playgroundContainer.style.width = WIDTH + 'px';
            playgroundContainer.style.height = HEIGHT - FOOTER_HEIGHT + 'px';

            sampleSwitcher.style.position = 'absolute';
            sampleSwitcher.style.top = TITLE_HEIGHT + 'px';
            sampleSwitcher.style.left = GLOBAL_PADDING + 'px';

            typingContainer.style.position = 'absolute';
            typingContainer.style.top = GLOBAL_PADDING + TITLE_HEIGHT + SWITCHER_HEIGHT + 'px';
            typingContainer.style.left = GLOBAL_PADDING + 'px';
            typingContainer.style.width = HALF_WIDTH + 'px';
            typingContainer.style.height = REMAINING_HEIGHT + 'px';

            tabArea.style.position = 'absolute';
            tabArea.style.boxSizing = 'border-box';
            tabArea.style.top = 0;
            tabArea.style.left = 0;
            tabArea.style.width = HALF_WIDTH + 'px';
            tabArea.style.height = TABS_HEIGHT + 'px';

            editorContainer.style.position = 'absolute';
            editorContainer.style.boxSizing = 'border-box';
            editorContainer.style.top = TABS_HEIGHT + 'px';
            editorContainer.style.left = 0;
            editorContainer.style.width = HALF_WIDTH + 'px';
            editorContainer.style.height = REMAINING_HEIGHT - TABS_HEIGHT + 'px';

            if (editor) {
                editor.layout({
                    width: HALF_WIDTH - 2,
                    height: REMAINING_HEIGHT - TABS_HEIGHT - 1
                });
            }

            runContainer.style.position = 'absolute';
            runContainer.style.top = GLOBAL_PADDING + TITLE_HEIGHT + SWITCHER_HEIGHT + TABS_HEIGHT + 'px';
            runContainer.style.left = GLOBAL_PADDING + INNER_PADDING + HALF_WIDTH + 'px';
            runContainer.style.width = HALF_WIDTH + 'px';
            runContainer.style.height = REMAINING_HEIGHT - TABS_HEIGHT + 'px';

            if (output) {
                output.layout({
                    width: HALF_WIDTH - 2,
                    height: REMAINING_HEIGHT - TABS_HEIGHT - 1
                });
            }
        }

        // create the typing side
        var typingContainer = document.createElement('div');
        typingContainer.className = 'typingContainer';

        var tabArea = (function () {
            var tabArea = document.createElement('div');
            tabArea.className = 'tabArea';

            var runLabel = 'Press ' + (isMac ? 'CMD + return' : 'CTRL + Enter') + ' to run the code.';
            var runBtn = document.createElement('button');
            runBtn.className = 'action run';
            runBtn.setAttribute('role', 'button');
            runBtn.setAttribute('aria-label', runLabel);
            runBtn.appendChild(document.createTextNode('Run'));
            runBtn.onclick = function () {
                run();
            };
            tabArea.appendChild(runBtn);

            return tabArea;
        })();

        var editorContainer = document.createElement('div');
        editorContainer.className = 'editor-container';

        typingContainer.appendChild(tabArea);
        typingContainer.appendChild(editorContainer);

        var runContainer = document.createElement('div');
        runContainer.className = 'run-container';

        var sampleSwitcher = document.createElement('select');
        var sampleChapter;
        PLAY_SAMPLES.forEach(function (sample) {
            if (!sampleChapter || sampleChapter.label !== sample.chapter) {
                sampleChapter = document.createElement('optgroup');
                sampleChapter.label = sample.chapter;
                sampleSwitcher.appendChild(sampleChapter);
            }
            var sampleOption = document.createElement('option');
            sampleOption.value = sample.id;
            sampleOption.appendChild(document.createTextNode(sample.name));
            sampleChapter.appendChild(sampleOption);
        });
        sampleSwitcher.className = 'sample-switcher';

        var LOADED_SAMPLES = [];
        function findLoadedSample(sampleId) {
            for (var i = 0; i < LOADED_SAMPLES.length; i++) {
                var sample = LOADED_SAMPLES[i];
                if (sample.id === sampleId) {
                    return sample;
                }
            }
            return null;
        }

        function findSamplePath(sampleId) {
            for (var i = 0; i < PLAY_SAMPLES.length; i++) {
                var sample = PLAY_SAMPLES[i];
                if (sample.id === sampleId) {
                    return sample.path;
                }
            }
            return null;
        }

        function loadSample(sampleId, callback) {
            var sample = findLoadedSample(sampleId);
            if (sample) {
                return callback(null, sample);
            }

            var samplePath = findSamplePath(sampleId);
            if (!samplePath) {
                return callback(new Error('sample not found'));
            }


            var py = xhr(samplePath).then(function (response) {
                return response.responseText;
            });
            Promise.all([py]).then(
                function (_) {
                    var py = _[0];
                    LOADED_SAMPLES.push({
                        id: sampleId,
                        py: py,
                    });
                    return callback(null, findLoadedSample(sampleId));
                },
                function (err) {
                    callback(err, null);
                }
            );
        }

        sampleSwitcher.onchange = function () {
            var sampleId = sampleSwitcher.options[sampleSwitcher.selectedIndex].value;
            window.location.hash = sampleId;
        };

        var playgroundContainer = document.getElementById('playground');

        layout();
        window.onresize = layout;

        playgroundContainer.appendChild(sampleSwitcher);
        playgroundContainer.appendChild(typingContainer);
        playgroundContainer.appendChild(runContainer);

        sourceModel = monaco.editor.createModel('', 'python');
        outputModel = monaco.editor.createModel('', 'bash');

        editor = monaco.editor.create(editorContainer, {
            model: sourceModel,
            minimap: {
                enabled: false
            },
            language: 'python',
            fontSize: "16px",
        });

        output = monaco.editor.create(runContainer, {
            model: outputModel,
            // readOnly: true,
            minimap: {
                enabled: false
            },
            language: 'python',
            fontSize: "16px",
        });

        var currentToken = 0;
        function parseHash(firstTime) {
            var sampleId = window.location.hash.replace(/^#/, '');
            if (!sampleId) {
                sampleId = PLAY_SAMPLES[0].id;
            }

            if (firstTime) {
                for (var i = 0; i < sampleSwitcher.options.length; i++) {
                    var opt = sampleSwitcher.options[i];
                    if (opt.value === sampleId) {
                        sampleSwitcher.selectedIndex = i;
                        break;
                    }
                }
            }

            var myToken = ++currentToken;
            loadSample(sampleId, function (err, sample) {
                if (err) {
                    alert('Sample not found! ' + err.message);
                    return;
                }
                if (myToken !== currentToken) {
                    return;
                }
                sourceModel.setValue(sample.py);
                editor.setScrollTop(0);
            });
        }
        window.onhashchange = parseHash;
        parseHash(true);

        async function initPyodide() {
            globalThis.pyodideWorker = new Worker('./webworker.js');
            pyodideWorker.onmessage = (e) => onPyodideMessage(e);
        }

        function run() {
            doRun();
        }

        editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, run);
        window.addEventListener('keydown', function keyDown(ev) {
            if ((isMac && !ev.metaKey) || !ev.ctrlKey) {
                return;
            }

            if (ev.shiftKey || ev.altKey || ev.keyCode !== 13) {
                return;
            }

            ev.preventDefault();
            run();
        });
    }

    function onPyodideMessage(event) {
        const data = event.data;
        switch (data.type) {
            case 'initialized':
                appendOutput('Pyodide Python runtime initialization complete\n');
                console.log(`[PyodideWorker] Initialize finished`);
                break;
            case 'output':
                appendOutput(data.text);
                console.log(data.text);
                break;
            case 'exec_start':
                console.log(`[PyodideWorker] Execution start #${data.id}`);
                break;
            case 'exec_finished':
                console.log(`[PyodideWorker] Execution finished #${data.id}`);
                break;
            case 'exec_error':
                console.error(`[PyodideWorker] Execution error in #${data.id}: ${data.error}`);
                break;
        }
    }

    function appendOutput(text) {
        const lineCount = output.getModel().getLineCount();
        const lastLineLength = output.getModel().getLineMaxColumn(lineCount);
        const range = new monaco.Range(
            lineCount,
            lastLineLength,
            lineCount,
            lastLineLength
        );
        const id = { major: 1, minor: 1 };
        const op = {
            identifier: id,
            range: range,
            text: text,
            forceMoveMarkers: true
        };

        output.updateOptions({readOnly: false});
        output.executeEdits("append-text", [op]);
        output.revealLine(lineCount)
        output.updateOptions({readOnly: true});
    }

    function doRun() {
        id = (id + 1) % Number.MAX_SAFE_INTEGER;
        let pysource = editor.getValue();
        pyodideWorker.postMessage({
            type: 'execute',
            id: id,
            data: pysource,
        });
    }

    var preloaded = {};
    (function () {
        var elements = Array.prototype.slice.call(document.querySelectorAll('pre[data-preload]'), 0);

        elements.forEach(function (el) {
            var path = el.getAttribute('data-preload');
            preloaded[path] = el.innerText || el.textContent;
            el.parentNode.removeChild(el);
        });
    })();

    function xhr(url) {
        if (preloaded[url]) {
            return Promise.resolve({
                responseText: preloaded[url]
            });
        }

        var req = null;
        return new Promise(
            function (c, e) {
                req = new XMLHttpRequest();
                req.onreadystatechange = function () {
                    if (req._canceled) {
                        return;
                    }

                    if (req.readyState === 4) {
                        if ((req.status >= 200 && req.status < 300) || req.status === 1223) {
                            c(req);
                        } else {
                            e(req);
                        }
                        req.onreadystatechange = function () {};
                    }
                };

                req.open('GET', url, true);
                req.responseType = '';

                req.send(null);
            },
            function () {
                req._canceled = true;
                req.abort();
            }
        );
    }
})();
