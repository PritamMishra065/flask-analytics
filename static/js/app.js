// API Base URL - uses current origin
const API_BASE = window.location.origin;

// Stats Form Handler - connects to GET /stats
document.getElementById('statsForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const form = e.target;
    const submitBtn = form.querySelector('button[type="submit"]');
    const btnText = submitBtn.querySelector('.btn-text');
    const btnLoader = submitBtn.querySelector('.btn-loader');
    
    const siteId = document.getElementById('siteId').value.trim();
    const date = document.getElementById('date').value;
    
    // Disable button and show loading
    submitBtn.disabled = true;
    btnText.style.display = 'none';
    btnLoader.style.display = 'inline';
    
    try {
        const params = new URLSearchParams({ site_id: siteId });
        if (date) {
            params.append('date', date);
        }
        
        const response = await fetch(`${API_BASE}/stats?${params}`);
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Failed to fetch stats');
        }
        
        // Display stats
        displayStats(data);
        
    } catch (error) {
        alert('Error: ' + error.message);
        console.error('Stats fetch error:', error);
    } finally {
        // Re-enable button
        submitBtn.disabled = false;
        btnText.style.display = 'inline';
        btnLoader.style.display = 'none';
    }
});

// Event Form Handler - connects to POST /event
document.getElementById('eventForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const form = e.target;
    const submitBtn = form.querySelector('button[type="submit"]');
    const btnText = submitBtn.querySelector('.btn-text');
    const btnLoader = submitBtn.querySelector('.btn-loader');
    const statusDiv = document.getElementById('eventStatus');
    
    const formData = {
        site_id: document.getElementById('eventSiteId').value.trim(),
        event_type: document.getElementById('eventType').value.trim(),
    };
    
    const path = document.getElementById('path').value.trim();
    const userId = document.getElementById('userId').value.trim();
    
    if (path) formData.path = path;
    if (userId) formData.user_id = userId;
    
    // Disable button and show loading
    submitBtn.disabled = true;
    btnText.style.display = 'none';
    btnLoader.style.display = 'inline';
    statusDiv.style.display = 'none';
    
    try {
        const response = await fetch(`${API_BASE}/event`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Failed to send event');
        }
        
        // Show success message
        statusDiv.textContent = 'Event sent successfully!';
        statusDiv.className = 'status-message success';
        statusDiv.style.display = 'block';
        
        // Clear form
        form.reset();
        
        // Hide message after 3 seconds
        setTimeout(() => {
            statusDiv.style.display = 'none';
        }, 3000);
        
    } catch (error) {
        statusDiv.textContent = 'Error: ' + error.message;
        statusDiv.className = 'status-message error';
        statusDiv.style.display = 'block';
        console.error('Event send error:', error);
    } finally {
        // Re-enable button
        submitBtn.disabled = false;
        btnText.style.display = 'inline';
        btnLoader.style.display = 'none';
    }
});

// Display Stats Function - updates UI with API response
function displayStats(data) {
    // Show stats section
    const statsSection = document.getElementById('statsSection');
    statsSection.style.display = 'block';
    
    // Update stat values - using total_views from API
    document.getElementById('totalViews').textContent = formatNumber(data.total_views || 0);
    document.getElementById('uniqueUsers').textContent = formatNumber(data.unique_users || 0);
    
    // Update query info
    document.getElementById('querySiteId').textContent = data.site_id || '-';
    document.getElementById('queryDate').textContent = data.date || '-';
    
    // Update top paths
    const topPathsDiv = document.getElementById('topPaths');
    topPathsDiv.innerHTML = '';
    
    if (data.top_paths && data.top_paths.length > 0) {
        data.top_paths.forEach((item, index) => {
            const pathItem = document.createElement('div');
            pathItem.className = 'path-item';
            pathItem.innerHTML = `
                <div class="path-info">
                    <span class="path-rank">#${index + 1}</span>
                    <span class="path">${escapeHtml(item.path || '/')}</span>
                </div>
                <span class="views">${formatNumber(item.views)} views</span>
            `;
            topPathsDiv.appendChild(pathItem);
        });
    } else {
        topPathsDiv.innerHTML = '<p style="color: var(--text-secondary); padding: 20px; text-align: center;">No paths found for this date.</p>';
    }
    
    // Scroll to stats section
    statsSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Helper function to escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Format number with commas
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

// Set today's date as default if date input is empty
window.addEventListener('DOMContentLoaded', () => {
    const dateInput = document.getElementById('date');
    if (!dateInput.value) {
        const today = new Date().toISOString().split('T')[0];
        dateInput.value = today;
    }
});
