<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>URL Processor</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            background-color: #f8f9fa;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .container {
            max-width: 600px;
            padding: 20px;
        }
        .card {
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .card-header {
            background-color: #007bff;
            color: white;
            border-radius: 15px 15px 0 0 !important;
            padding: 15px;
        }
        .form-control {
            border-radius: 10px;
            padding: 12px;
        }
        .btn {
            border-radius: 10px;
            padding: 12px 25px;
        }
        #result {
            margin-top: 20px;
            padding: 15px;
            border-radius: 10px;
            display: none;
        }
        .success {
            background-color: #d4edda;
            border: 1px solid #c3e6cb;
        }
        .error {
            background-color: #f8d7da;
            border: 1px solid #f5c6cb;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <div class="card-header text-center">
                <h3 class="mb-0">URL Processor</h3>
                <div class="text-end position-absolute top-0 end-0 p-2">
                    <a href="{{ url_for('logout') }}" class="btn btn-outline-light btn-sm">Logout</a>
                </div>
            </div>
            <div class="card-body">
                <form id="urlForm">
                    <div class="mb-3">
                        <label for="url" class="form-label">Enter URL</label>
                        <input type="url" class="form-control" id="url" name="url" required placeholder="https://runurl.in/xxxx or https://seturl.in/xxxx">
                        <div class="form-text text-muted">Supported domains: runurl.in and seturl.in</div>
                    </div>
                    <div class="text-center">
                        <button type="submit" class="btn btn-primary" id="submitBtn">Process URL</button>
                    </div>
                </form>
                <div id="result"></div>
            </div>
        </div>
    </div>

    <script>
        let currentSessionId = null;
        let retryCount = 0;
        let isRefreshing = false;
        let pageJustLoaded = true;

        // Add post-refresh delay on page load
        window.addEventListener('load', function() {
            if (sessionStorage.getItem('justRefreshed') === 'true') {
                // Clear the flag
                sessionStorage.removeItem('justRefreshed');
                
                // Disable all form elements
                const form = document.getElementById('urlForm');
                const inputs = form.querySelectorAll('input, button');
                inputs.forEach(input => input.disabled = true);
                
                // Create overlay with 3-second countdown
                const overlay = document.createElement('div');
                overlay.style.position = 'fixed';
                overlay.style.top = '0';
                overlay.style.left = '0';
                overlay.style.width = '100%';
                overlay.style.height = '100%';
                overlay.style.backgroundColor = 'rgba(0, 0, 0, 0.7)';
                overlay.style.display = 'flex';
                overlay.style.justifyContent = 'center';
                overlay.style.alignItems = 'center';
                overlay.style.zIndex = '1000';
                overlay.id = 'postRefreshOverlay';
                
                let secondsLeft = 5;
                overlay.innerHTML = `
                    <div class="text-center text-white">
                        <h3>Page Refreshed!</h3>
                        <p>You can continue in ${secondsLeft} seconds</p>
                    </div>
                `;
                
                document.body.appendChild(overlay);
                
                // Update countdown
                const countdownInterval = setInterval(() => {
                    secondsLeft--;
                    if (secondsLeft <= 0) {
                        clearInterval(countdownInterval);
                        document.body.removeChild(overlay);
                        inputs.forEach(input => input.disabled = false);
                    } else {
                        overlay.innerHTML = `
                            <div class="text-center text-white">
                                <h3>Page Refreshed!</h3>
                                <p>You can continue in ${secondsLeft} seconds</p>
                            </div>
                        `;
                    }
                }, 1000);
            }
        });

        document.getElementById('urlForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            // Don't allow form submission during refresh cooldown
            if (isRefreshing) {
                return;
            }
            
            const submitBtn = document.getElementById('submitBtn');
            const resultDiv = document.getElementById('result');
            const url = document.getElementById('url').value;

            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...';
            resultDiv.style.display = 'none';

            try {
                const formData = new FormData();
                formData.append('url', url);
                if (currentSessionId) {
                    formData.append('retry', 'true');
                    formData.append('session_id', currentSessionId);
                }

                const response = await fetch('/process_url', {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();
                
                resultDiv.style.display = 'block';
                if (data.status === 'cloudflare') {
                    resultDiv.className = 'error';
                    // Update retry count from server response
                    retryCount = data.retry_count || 0;
                    
                    let buttonsHtml = '';
                    
                    // Max retry attempts is 3 (since we changed it in app.py)
                    if (retryCount >= 3) {
                        // Only show refresh button after 3 attempts
                        buttonsHtml = `
                            <div class="text-center">
                                <button onclick="refreshPage()" class="btn btn-warning mt-2">Refresh Page</button>
                            </div>
                        `;
                    } else {
                        buttonsHtml = `
                            <div class="text-center">
                                <button onclick="retryProcess()" class="btn btn-primary mt-2">Try Again</button>
                            </div>
                        `;
                    }
                    
                    resultDiv.innerHTML = `
                        <div class="alert alert-danger">${data.message}</div>
                        ${buttonsHtml}
                    `;
                    currentSessionId = data.session_id;
                } else if (data.status === 'success') {
                    resultDiv.className = 'success';
                    resultDiv.innerHTML = `
                        <h5>Processed URL:</h5>
                        <div class="input-group mb-3 mt-2">
                            <input type="text" class="form-control" value="${data.url}" id="resultUrl" readonly>
                            <button class="btn btn-outline-secondary" type="button" onclick="copyToClipboard()">Copy</button>
                        </div>
                        <div class="text-center">
                            <a href="${data.url}" target="_blank" class="btn btn-success">Open Link</a>
                        </div>
                    `;
                    currentSessionId = null;
                    retryCount = 0;
                } else if (data.status === 'error') {
                    resultDiv.className = 'error';
                    // Update retry count from server response
                    retryCount = data.retry_count || 0;
                    
                    let buttonsHtml = '';
                    
                    // Max retry attempts is 3 (since we changed it in app.py)
                    if (retryCount >= 3) {
                        // Only show refresh button after 3 attempts
                        buttonsHtml = `
                            <div class="text-center">
                                <button onclick="refreshPage()" class="btn btn-warning mt-2">Refresh Page</button>
                            </div>
                        `;
                    } else {
                        buttonsHtml = `
                            <div class="text-center">
                                <button onclick="retryProcess()" class="btn btn-primary mt-2">Try Again</button>
                            </div>
                        `;
                    }
                    
                    resultDiv.innerHTML = `
                        <div class="alert alert-danger">${data.message}</div>
                        ${buttonsHtml}
                    `;
                    currentSessionId = data.session_id;
                }
            } catch (error) {
                resultDiv.style.display = 'block';
                resultDiv.className = 'error';
                resultDiv.innerHTML = `
                    <div class="alert alert-danger">An error occurred. Please try again.</div>
                    <div class="text-center">
                        <button onclick="retryProcess()" class="btn btn-primary mt-2">Try Again</button>
                    </div>
                `;
            } finally {
                submitBtn.disabled = false;
                submitBtn.innerHTML = 'Process URL';
            }
        });

        function retryProcess() {
            if (currentSessionId) {
                document.getElementById('urlForm').dispatchEvent(new Event('submit'));
            } else {
                currentSessionId = null;
                retryCount = 0;
                document.getElementById('urlForm').dispatchEvent(new Event('submit'));
            }
        }

        function refreshPage() {
            // Set refreshing state
            isRefreshing = true;
            
            // Disable all inputs and show countdown
            const form = document.getElementById('urlForm');
            const resultDiv = document.getElementById('result');
            const inputs = form.querySelectorAll('input, button');
            
            inputs.forEach(input => input.disabled = true);
            
            // Create countdown overlay
            const overlay = document.createElement('div');
            overlay.style.position = 'fixed';
            overlay.style.top = '0';
            overlay.style.left = '0';
            overlay.style.width = '100%';
            overlay.style.height = '100%';
            overlay.style.backgroundColor = 'rgba(0, 0, 0, 0.7)';
            overlay.style.display = 'flex';
            overlay.style.justifyContent = 'center';
            overlay.style.alignItems = 'center';
            overlay.style.zIndex = '1000';
            
            // Changed from 5 to 4 seconds
            let secondsLeft = 2;
            overlay.innerHTML = `
                <div class="text-center text-white">
                    <h3>Refreshing session...</h3>
                    <p>Please wait ${secondsLeft} seconds</p>
                </div>
            `;
            
            document.body.appendChild(overlay);
            
            // Update countdown every second
            const countdownInterval = setInterval(() => {
                secondsLeft--;
                if (secondsLeft <= 0) {
                    clearInterval(countdownInterval);
                    performRefresh();
                } else {
                    overlay.innerHTML = `
                        <div class="text-center text-white">
                            <h3>Refreshing session...</h3>
                            <p>Please wait ${secondsLeft} seconds</p>
                        </div>
                    `;
                }
            }, 1000);
            
            function performRefresh() {
                // Set a flag in sessionStorage to indicate page is refreshing
                sessionStorage.setItem('justRefreshed', 'true');
                
                // If we have a session ID, terminate it first
                if (currentSessionId) {
                    const formData = new FormData();
                    formData.append('session_id', currentSessionId);
                    
                    fetch('/reset_session', {
                        method: 'POST',
                        body: formData
                    }).finally(() => {
                        // Reload the page after delay
                        window.location.reload();
                    });
                } else {
                    // Just reload if no session
                    window.location.reload();
                }
            }
        }

        function copyToClipboard() {
            const resultUrl = document.getElementById('resultUrl');
            resultUrl.select();
            resultUrl.setSelectionRange(0, 99999);
            document.execCommand('copy');
            
            const copyBtn = document.querySelector('.input-group button');
            const originalText = copyBtn.innerHTML;
            copyBtn.innerHTML = 'Copied!';
            setTimeout(() => {
                copyBtn.innerHTML = originalText;
            }, 2000);
        }
    </script>
</body>
</html> 
