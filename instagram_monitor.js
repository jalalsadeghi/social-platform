// Instagram Upload Process Monitor
(() => {
    const LOG_PREFIX = '📝 [Instagram Monitor]';
    let logs = [];
    
    // Utility function to safely stringify objects
    const safeStringify = (obj) => {
        try {
            return JSON.stringify(obj, (key, value) => {
                if (value instanceof HTMLElement) {
                    return `HTMLElement: ${value.tagName} - ${value.className} - ${value.id}`;
                }
                if (value instanceof Function) {
                    return 'function';
                }
                return value;
            }, 2);
        } catch (e) {
            return String(obj);
        }
    };

    // Log function with timestamp
    const logWithTime = (type, message, data = null) => {
        const timestamp = new Date().toISOString();
        const logEntry = {
            timestamp,
            type,
            message,
            data: data ? safeStringify(data) : null
        };
        logs.push(logEntry);
        console.log(`${LOG_PREFIX} [${type}] ${message}`, data || '');
    };

    // Monitor DOM mutations
    const observeDOM = () => {
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                    mutation.addedNodes.forEach(node => {
                        if (node.nodeType === 1) { // ELEMENT_NODE
                            logWithTime('DOM_CHANGE', 'New element added', {
                                tagName: node.tagName,
                                className: node.className,
                                id: node.id,
                                attributes: Array.from(node.attributes || []).map(attr => ({
                                    name: attr.name,
                                    value: attr.value
                                }))
                            });
                        }
                    });
                }
            });
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true,
            attributes: true
        });
    };

    // Monitor network requests
    const monitorNetwork = () => {
        const originalFetch = window.fetch;
        window.fetch = async (...args) => {
            logWithTime('NETWORK', 'Fetch request initiated', { url: args[0], options: args[1] });
            try {
                const response = await originalFetch(...args);
                logWithTime('NETWORK', 'Fetch request completed', {
                    url: args[0],
                    status: response.status,
                    statusText: response.statusText
                });
                return response;
            } catch (error) {
                logWithTime('NETWORK_ERROR', 'Fetch request failed', {
                    url: args[0],
                    error: error.message
                });
                throw error;
            }
        };

        // Monitor XHR requests
        const originalXHR = window.XMLHttpRequest.prototype.open;
        window.XMLHttpRequest.prototype.open = function(...args) {
            this.addEventListener('load', () => {
                logWithTime('XHR', 'XHR request completed', {
                    method: args[0],
                    url: args[1],
                    status: this.status,
                    statusText: this.statusText
                });
            });
            return originalXHR.apply(this, args);
        };
    };

    // Monitor file input changes
    const monitorFileInputs = () => {
        document.addEventListener('change', (event) => {
            if (event.target.type === 'file') {
                const files = Array.from(event.target.files || []).map(file => ({
                    name: file.name,
                    type: file.type,
                    size: file.size,
                    lastModified: file.lastModified
                }));
                logWithTime('FILE_INPUT', 'File input change detected', {
                    inputId: event.target.id,
                    inputName: event.target.name,
                    files
                });
            }
        }, true);
    };

    // Monitor click events
    const monitorClicks = () => {
        document.addEventListener('click', (event) => {
            const element = event.target;
            logWithTime('CLICK', 'Click event detected', {
                element: {
                    tagName: element.tagName,
                    className: element.className,
                    id: element.id,
                    text: element.textContent?.trim(),
                    role: element.getAttribute('role'),
                    ariaLabel: element.getAttribute('aria-label')
                },
                path: event.path?.map(el => ({
                    tagName: el.tagName,
                    className: el.className,
                    id: el.id
                }))
            });
        }, true);
    };

    // Monitor state changes in video elements
    const monitorVideoElements = () => {
        const videoEvents = ['loadstart', 'loadedmetadata', 'loadeddata', 'canplay', 'canplaythrough', 'play', 'pause'];
        
        const observeVideo = (video) => {
            videoEvents.forEach(eventName => {
                video.addEventListener(eventName, () => {
                    logWithTime('VIDEO_EVENT', `Video ${eventName} event`, {
                        readyState: video.readyState,
                        currentTime: video.currentTime,
                        duration: video.duration,
                        paused: video.paused,
                        ended: video.ended,
                        networkState: video.networkState
                    });
                });
            });
        };

        // Monitor existing video elements
        document.querySelectorAll('video').forEach(observeVideo);

        // Monitor for new video elements
        new MutationObserver((mutations) => {
            mutations.forEach(mutation => {
                mutation.addedNodes.forEach(node => {
                    if (node.nodeName === 'VIDEO') {
                        observeVideo(node);
                    }
                });
            });
        }).observe(document.body, {
            childList: true,
            subtree: true
        });
    };

    // Initialize monitoring
    const init = () => {
        logWithTime('INIT', 'Instagram upload monitor initialized');
        observeDOM();
        monitorNetwork();
        monitorFileInputs();
        monitorClicks();
        monitorVideoElements();
    };

    // Export logs function
    window.exportInstagramMonitorLogs = () => {
        const exportData = {
            timestamp: new Date().toISOString(),
            userAgent: navigator.userAgent,
            logs
        };
        
        // Create and download logs file
        const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `instagram-upload-logs-${new Date().toISOString()}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        return exportData;
    };

    // Start monitoring
    init();
    console.log(`${LOG_PREFIX} Monitoring started. Use window.exportInstagramMonitorLogs() to export logs.`);
})(); 