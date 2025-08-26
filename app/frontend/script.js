// --- DOM Elements ---
const browseBtn = document.getElementById('browse-btn');
const folderPathInput = document.getElementById('folder-path');
const folderInput = document.getElementById('folder-input');
const searchInput = document.getElementById('search-input');
const searchBtn = document.getElementById('search-btn');
const forceAnalyzeBtn = document.getElementById('force-analyze-btn');
const resultsTableContainer = document.getElementById('results-table-container');
const resultsTbody = document.getElementById('results-tbody');
const noResultsMessage = document.getElementById('no-results');
const searchSection = document.getElementById('search-section');
const resumeDetailsModal = document.getElementById('resume-details-modal');
const detailsContent = document.getElementById('details-content');
const detailsCloseBtn = document.getElementById('details-close-btn');
const loadingIndicator = document.getElementById('loading-indicator');
const cacheStatus = document.getElementById('cache-status');
const cacheIndicators = document.getElementById('cache-indicators');
const processingInfo = document.getElementById('processing-info');
const resumeCountContainer = document.getElementById('resume-count');
const resumeCountNum = document.getElementById('resume-count-num');
const clearCurrentCacheBtn = document.getElementById('clear-current-cache-btn');
const clearAllCacheBtn = document.getElementById('clear-all-cache-btn');

// Global variable to store current cache key
let currentCacheKey = null;

// --- Functions ---
/**
 * Calls the backend API to parse resumes based on the provided folder path and skills.
 * @param {string} folderPath - The path of the folder to search.
 * @param {string} skills - Comma-separated skills to search for.
 * @param {boolean} forceAnalyze - Whether to force fresh analysis bypassing cache.
 * @returns {Promise<Object>} - A promise that resolves with the parsed data and cache info.
 */
async function parseResumesAPI(folderPath, skills, forceAnalyze = false) {
    console.log(`API Call: Parsing resumes from '${folderPath}' for skills: '${skills}', force: ${forceAnalyze}`);
    
    // Show the loader while the API call is in progress
    loadingIndicator.classList.remove('hidden');
    resultsTableContainer.classList.add('hidden');
    noResultsMessage.classList.add('hidden');
    cacheStatus.classList.add('hidden');
    
    // Hide the resume count while loading
    if (resumeCountContainer) resumeCountContainer.classList.add('hidden');

    // Add loading message for large datasets
    const loadingMessage = document.getElementById('loading-message');
    if (loadingMessage) {
        loadingMessage.textContent = forceAnalyze 
            ? 'Force analyzing resumes... This may take a while for large datasets.' 
            : 'Processing resumes... Please wait.';
    }

    let finalResponse = [];
    let cacheInfo = null;

    try {
        const response = await fetch('http://localhost:8000/parse-resume', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                dirPath: folderPath,
                query: skills,
                forceAnalyze: forceAnalyze,
            }),
        });

        if (response.ok) {
            const data = await response.json();
            
            if (data.error) {
                alert(`Error: ${data.error}`);
                finalResponse = [];
                cacheInfo = null;
            } else {
                finalResponse = data.result;
                cacheInfo = data.cache_info;
                
                // Log performance info for large datasets
                if (data.summary && data.summary.total_resumes_processed > 50) {
                    console.log('📊 Performance Summary:', data.summary);
                }
            }
        } else {
            const errorData = await response.json().catch(() => ({}));
            const errorMessage = errorData.error || 'Failed to fetch results. Please try again.';
            alert(errorMessage);
            finalResponse = [];
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred. Please check your connection and try again.');
        finalResponse = [];
    }

    loadingIndicator.classList.add('hidden'); // Hide loader
    return { result: finalResponse, cache_info: cacheInfo };
}

/**
 * Simulates calling the backend API to parse resumes.
 * In a real application, this would be a fetch() call to your Python server.
 * @param {string} folderPath - The path of the folder to search.
 * @param {string} skills - Comma-separated skills to search for.
 * @returns {Promise<Array<object>>} - A promise that resolves with the parsed data.
 */
function parseResumesAPIMock(folderPath, skills) {
    console.log(`API Call: Parsing resumes from '${folderPath}' for skills: '${skills}'`);
    
    // Show the loader while the API call is in progress
    loadingIndicator.classList.remove('hidden');
    resultsTableContainer.classList.add('hidden');
    noResultsMessage.classList.add('hidden');
    
    // Hide the resume count while loading
    if (resumeCountContainer) resumeCountContainer.classList.add('hidden');

    return new Promise((resolve) => {
        // Simulate network delay
        setTimeout(() => {
            // --- MOCK API RESPONSE ---
            // This is the sample JSON data you provided. In a real app,
            // this would come from the server.
            const mockResponse = [
                {
                    "name": "Stanley Sebastian",
                    "contact_number": "+919845928740",
                    "last_3_companies": ["Cognizant Technology Solutions", null, null],
                    "top_5_technical_skills": ["Angular", ".NET", ".NET Core", "C#", "ASP.NET"],
                    "source_file": "resume-1.docx"
                },
                {
                    "name": "Sudheer Kumar Sharma",
                    "contact_number": "9533123958",
                    "last_3_companies": ["Cognizant Technology Solutions Pvt Ltd", "Saven Nova Technology Pvt Ltd", "null"],
                    "top_5_technical_skills": ["angular", ".net core", ".net framework", "asp.net", "c#"],
                    "source_file": "resume-2.docx"
                },
                {
                    "name": "Jane Doe",
                    "contact_number": "555-123-4567",
                    "last_3_companies": ["Tech Solutions Inc.", "Innovate Corp.", "Startup LLC"],
                    "top_5_technical_skills": ["JavaScript", "React", "Node.js", "Python", "AWS"],
                    "source_file": "resume-3.pdf"
                }
            ];
            
            // Simulate filtering based on skills for a more realistic demo
            const skillList = skills.toLowerCase().split(',').map(s => s.trim()).filter(Boolean);
            const filteredResponse = skillList.length === 0 ? mockResponse : mockResponse.filter(resume => 
                resume.top_5_technical_skills.some(skill => 
                    skillList.includes(skill.toLowerCase())
                )
            );

            console.log('API Response:', filteredResponse);
            loadingIndicator.classList.add('hidden'); // Hide loader
            resolve(filteredResponse);
        }, 1500); // 1.5 second delay
    });
}

/**
 * Creates an HTML table row string for a single resume.
 * @param {object} resume - The resume data object from the API.
 * @returns {string} - The HTML string for the table row.
 */
function createResumeTableRow(resume) {
    // Format skills into styled badges
    const skillsHtml = (resume.top_5_technical_skills || []).map(skill => 
        `<span class="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium skill-badge mr-2 mb-1">${skill || 'N/A'}</span>`
    ).join('');

    // Format company list, filtering out null or "null" string values
    const companiesHtml = (resume.last_3_companies || [])
        .filter(company => company && company.toLowerCase() !== 'null')
        .map(company => `<li class="text-gray-100 text-xs mb-1">${company}</li>`).join('');

    // Format match score with color coding
    const score = resume.match_score || 0;
    let scoreClass = 'bg-gray-600 text-gray-300';
    let scoreIcon = 'fas fa-minus';
    
    if (score >= 80) {
        scoreClass = 'bg-green-600 text-green-100';
        scoreIcon = 'fas fa-star';
    } else if (score >= 65) {
        scoreClass = 'bg-blue-600 text-blue-100';
        scoreIcon = 'fas fa-thumbs-up';
    } else if (score >= 50) {
        scoreClass = 'bg-yellow-600 text-yellow-100';
        scoreIcon = 'fas fa-check';
    } else if (score >= 30) {
        scoreClass = 'bg-orange-600 text-orange-100';
        scoreIcon = 'fas fa-exclamation';
    } else {
        scoreClass = 'bg-red-600 text-red-100';
        scoreIcon = 'fas fa-times';
    }

    // Prepare data for the details modal
    const resumeDataJson = JSON.stringify(resume).replace(/"/g, '&quot;');

    return `
        <tr class="hover:bg-gray-50 hover:bg-opacity-5 transition-colors duration-150">
            <td class="px-4 py-3">
                <div class="font-medium text-gray-100 text-sm">${resume.name || '—'}</div>
            </td>
            <td class="px-4 py-3">
                <span class="text-gray-400 text-sm font-mono">${resume.contact_number || '—'}</span>
            </td>
            <td class="px-4 py-3">
                <span class="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-blue-600 bg-opacity-20 text-blue-400">
                    ${resume.years_of_experience || '—'} years
                </span>
            </td>
            <td class="px-4 py-3">
                <ul class="company-list space-y-1 text-xs">
                    ${companiesHtml || '<li class="text-gray-400">—</li>'}
                </ul>
            </td>
            <td class="px-4 py-3">
                <div class="flex flex-wrap">
                    ${skillsHtml || '<span class="text-gray-400 text-xs">—</span>'}
                </div>
            </td>
            <td class="px-4 py-3 text-center">
                <div class="flex flex-col items-center space-y-1">
                    <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold ${scoreClass}">
                        <i class="${scoreIcon} mr-1"></i>
                        ${score}%
                    </span>
                </div>
            </td>
            <td class="px-4 py-3 text-center">
                <div class="relative flex justify-center">
                    <button class="details-btn flex items-center px-2 py-1 text-gray-400 hover:text-blue-400 hover:bg-gray-900 rounded transition-colors cursor-pointer"
                            data-resume="${resumeDataJson}">
                        <i class="fas fa-arrow-up-right-from-square mr-2"></i>
                        <span class="text-xs">View</span>
                    </button>
                </div>
            </td>
        </tr>
    `;
}

/**
 * Update the resume count tag in the header
 * @param {number} count - Number of analyzed resumes
 */
function updateResumeCount(count) {
    if (!resumeCountContainer || !resumeCountNum) return;
    if (count > 0) {
        resumeCountNum.textContent = count;
        resumeCountContainer.classList.remove('hidden');
    } else {
        resumeCountContainer.classList.add('hidden');
    }
}

/**
 * Display cache status information in the UI
 * @param {object} cacheInfo - Cache information from the backend
 */
function displayCacheStatus(cacheInfo) {
    if (!cacheInfo) {
        cacheStatus.classList.add('hidden');
        return;
    }

    // Store current cache key globally for clearing current cache
    currentCacheKey = cacheInfo.cache_key;

    // Clear previous content
    cacheIndicators.innerHTML = '';
    processingInfo.innerHTML = '';

    // Vector cache indicator
    const vectorCacheIcon = document.createElement('div');
    vectorCacheIcon.className = `flex items-center space-x-2 px-2 py-1 rounded-2xl text-xs font-medium ${
        cacheInfo.vector_cache_hit 
            ? 'cache-hit' 
            : 'cache-miss'
    }`;
    vectorCacheIcon.innerHTML = `
        <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
            <path d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z"></path>
        </svg>
        <span>Vector: ${cacheInfo.vector_cache_hit ? 'Cached' : 'Fresh'}</span>
    `;
    cacheIndicators.appendChild(vectorCacheIcon);

    // Gemini cache indicator
    const geminiCacheIcon = document.createElement('div');
    geminiCacheIcon.className = `flex items-center space-x-2 px-2 py-1 rounded-2xl text-xs font-medium ${
        cacheInfo.gemini_cache_hit 
            ? 'cache-hit' 
            : 'cache-miss'
    }`;
    geminiCacheIcon.innerHTML = `
        <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clip-rule="evenodd"></path>
        </svg>
        <span>Gemini: ${cacheInfo.gemini_cache_hit ? 'Cached' : 'Fresh'}</span>
    `;
    cacheIndicators.appendChild(geminiCacheIcon);

    // Batch processing indicator (if applicable)
    if (cacheInfo.total_batches && cacheInfo.total_batches > 1) {
        const batchIcon = document.createElement('div');
        batchIcon.className = `flex items-center space-x-2 px-2 py-1 rounded-md text-xs font-medium ${
            cacheInfo.batches_processed === cacheInfo.total_batches 
                ? 'bg-green-600 bg-opacity-20 text-green-400' 
                : 'bg-yellow-600 bg-opacity-20 text-yellow-400'
        }`;
        batchIcon.innerHTML = `
            <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                <path d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z"></path>
            </svg>
            <span>Batches: ${cacheInfo.batches_processed}/${cacheInfo.total_batches}</span>
        `;
        cacheIndicators.appendChild(batchIcon);
    }

    // Processing info with enhanced metrics
    let infoText = `${cacheInfo.total_resumes} resumes → ${cacheInfo.filtered_resumes} filtered`;
    if (cacheInfo.processing_time) {
        infoText += ` • ${cacheInfo.processing_time}s`;
        
        // Add throughput for large datasets
        if (cacheInfo.total_resumes > 10) {
            const throughput = (cacheInfo.total_resumes / cacheInfo.processing_time).toFixed(1);
            infoText += ` (${throughput}/s)`;
        }
    }
    if (cacheInfo.cache_key) {
        infoText += ` • ${cacheInfo.cache_key.substring(0, 8)}...`;
    }
    
    processingInfo.textContent = infoText;
    cacheStatus.classList.remove('hidden');
}

/**
 * Show comprehensive resume details modal
 * @param {object} resume - Complete resume data object
 */
function showResumeDetails(resume) {
    const modal = resumeDetailsModal;
    const content = detailsContent;
    
    // Color code the score
    const score = resume.match_score || 0;
    let scoreColor = 'text-gray-400';
    if (score >= 80) scoreColor = 'text-green-400';
    else if (score >= 65) scoreColor = 'text-blue-400';
    else if (score >= 50) scoreColor = 'text-yellow-400';
    else if (score >= 30) scoreColor = 'text-orange-400';
    else scoreColor = 'text-red-400';
    
    // Format skills
    const skillsHtml = (resume.top_5_technical_skills || [])
        .map(skill => `<span class="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium skill-badge mr-2 mb-2">${skill}</span>`)
        .join('');
    
    // Format companies
    const companiesHtml = (resume.last_3_companies || [])
        .filter(company => company && company.toLowerCase() !== 'null')
        .map(company => `<li class="text-gray-100 text-sm mb-2 flex items-center"><div class="w-1.5 h-1.5 bg-blue-400 rounded-full mr-3"></div>${company}</li>`)
        .join('') || '<li class="text-gray-400 text-sm">No company information available</li>';
    
    content.innerHTML = `
        <!-- Header Section -->
        <div class="bg-gray-900 rounded-lg p-6 mb-6">
            <div class="flex items-start justify-between">
                <div>
                    <h3 class="text-2xl font-bold text-white mb-2">${resume.name || 'Unknown'}</h3>
                    <div class="flex items-center space-x-4 text-sm text-gray-300">
                        <span class="flex items-center">
                            <i class="fas fa-phone mr-2 text-blue-400"></i>
                            ${resume.contact_number || 'Not provided'}
                        </span>
                        <span class="flex items-center">
                            <i class="fas fa-file-alt mr-2 text-blue-400"></i>
                            ${resume.source_file || 'Unknown file'}
                        </span>
                        <span class="flex items-center">
                            <i class="fas fa-clock mr-2 text-blue-400"></i>
                            ${resume.years_of_experience || 0} years experience
                        </span>
                    </div>
                </div>
                <div class="text-center">
                    <div class="text-4xl font-bold ${scoreColor} mb-1">${score}%</div>
                    <div class="text-xs text-gray-400 uppercase tracking-wide">Match Score</div>
                </div>
            </div>
        </div>

        <!-- Two Column Layout -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <!-- Left Column -->
            <div class="space-y-6">
                <!-- Score Breakdown -->
                <div class="bg-gray-900 rounded-lg p-4">
                    <h4 class="text-sm font-semibold text-gray-300 mb-3 flex items-center">
                        <i class="fas fa-chart-line mr-2 text-blue-400"></i>
                        Score Breakdown
                    </h4>
                    <div class="bg-gray-800 rounded-md p-3">
                        <p class="text-gray-100 text-sm leading-relaxed">${resume.score_breakdown || 'No detailed breakdown available.'}</p>
                    </div>
                    <div class="mt-3 text-xs text-gray-400 border-t border-gray-700 pt-3">
                        <strong>Scoring Criteria:</strong> Skill Relevance (40%), Experience (20%), Company Quality (15%), Project Complexity (15%), Education (10%)
                    </div>
                </div>

                <!-- Key Skills -->
                <div class="bg-gray-900 rounded-lg p-4">
                    <h4 class="text-sm font-semibold text-gray-300 mb-3 flex items-center">
                        <i class="fas fa-code mr-2 text-blue-400"></i>
                        Key Technical Skills
                    </h4>
                    <div class="flex flex-wrap">
                        ${skillsHtml || '<span class="text-gray-400 text-sm">No skills information available</span>'}
                    </div>
                </div>
            </div>

            <!-- Right Column -->
            <div class="space-y-6">
                <!-- Professional Summary -->
                <div class="bg-gray-900 rounded-lg p-4">
                    <h4 class="text-sm font-semibold text-gray-300 mb-3 flex items-center">
                        <i class="fas fa-user-circle mr-2 text-blue-400"></i>
                        Professional Summary
                    </h4>
                    <div class="bg-gray-800 rounded-md p-3">
                        <p class="text-gray-100 text-sm leading-relaxed">${resume.summary || 'No summary available.'}</p>
                    </div>
                </div>

                <!-- Past Organizations -->
                <div class="bg-gray-900 rounded-lg p-4">
                    <h4 class="text-sm font-semibold text-gray-300 mb-3 flex items-center">
                        <i class="fas fa-building mr-2 text-blue-400"></i>
                        Past Organizations
                    </h4>
                    <ul class="space-y-2">
                        ${companiesHtml}
                    </ul>
                </div>
            </div>
        </div>
    `;
    
    modal.classList.remove('hidden');
}

/**
 * Renders a list of resumes to the table or shows a 'no results' message.
 * @param {Array<object>} resumes - An array of resume objects to display.
 * @param {number} totalCount - Total number of resumes in the folder.
 */
function renderResumes(resumes, totalCount = null) {
    resultsTbody.innerHTML = ''; // Clear previous results

    // Update the resume count tag with total count if available, otherwise use filtered count
    updateResumeCount(totalCount !== null ? totalCount : resumes.length);

    if (resumes.length === 0) {
        noResultsMessage.classList.remove('hidden');
        resultsTableContainer.classList.add('hidden');
    } else {
        noResultsMessage.classList.add('hidden');
        resultsTableContainer.classList.remove('hidden');
        
        // Sort resumes by match_score in descending order if score is available
        const sortedResumes = [...resumes].sort((a, b) => {
            const scoreA = a.match_score || 0;
            const scoreB = b.match_score || 0;
            return scoreB - scoreA; // Descending order (highest score first)
        });
        
        const rowsHtml = sortedResumes.map(createResumeTableRow).join('');
        resultsTbody.innerHTML = rowsHtml;
        addDetailsEventListeners(); // Ensure details buttons have event listeners
    }
}

/**
 * Clear cache via API call
 * @param {string} cacheType - Type of cache to clear: "current" or "all"
 * @param {string} cacheKey - Cache key for current cache (optional)
 */
async function clearCache(cacheType, cacheKey = null) {
    try {
        console.log(`Clearing ${cacheType} cache...`);
        
        const requestBody = { type: cacheType };
        if (cacheKey) {
            requestBody.cache_key = cacheKey;
        }
        
        const response = await fetch('http://localhost:8000/clear-cache', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody),
        });

        if (response.ok) {
            const data = await response.json();
            if (data.success) {
                alert(`${data.message}`);
                console.log(`✅ ${cacheType} cache cleared successfully`);
                
                // Hide cache status after clearing all cache
                if (cacheType === 'all') {
                    cacheStatus.classList.add('hidden');
                }
            } else {
                alert(`Failed to clear cache: ${data.error}`);
                console.error(`❌ Failed to clear ${cacheType} cache:`, data.error);
            }
        } else {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
    } catch (error) {
        console.error(`❌ Error clearing ${cacheType} cache:`, error);
        alert(`An error occurred while clearing ${cacheType} cache. Please check the console.`);
    }
}

// --- Event Listeners ---

/**
 * Handle "Browse" button click. In a real app, this would open a
 * file dialog. Here, we simulate selecting a folder to enable the UI.
 */
browseBtn.addEventListener('click', () => {
    // This is a simulation. Browser security prevents scripts from
    // programmatically opening a folder picker and getting the path directly.
    folderPathInput.value = folderPathInput.value.replace(/\//g, '//'); // 'C:\\POC\\indranilweb\\ai-resume-parser\\app\\resumes' // 'C:\\Users\\DemoUser\\Documents\\Resumes'; // Mock path
    // folderInput.click();
    
    // Enable step 2 when folder is selected
    enableStep2();
    searchInput.focus();
});

/**
 * Enable Step 2 controls when folder is selected
 */
function enableStep2() {
    const searchSection = document.getElementById('search-section');
    const searchInput = document.getElementById('search-input');
    const searchBtn = document.getElementById('search-btn');
    const forceAnalyzeBtn = document.getElementById('force-analyze-btn');
    
    // Remove disabled styling and enable controls
    searchSection.classList.remove('opacity-50', 'pointer-events-none');
    searchSection.classList.add('opacity-100');
    
    // Update step 2 indicator color
    const step2Number = searchSection.querySelector('.w-6.h-6');
    const step2Icon = searchSection.querySelector('.fas');
    
    step2Number.classList.remove('bg-gray-500');
    step2Number.classList.add('bg-blue-600');
    
    step2Icon.classList.remove('text-gray-500');
    step2Icon.classList.add('text-blue-400');
    
    // Enable form controls
    searchInput.disabled = false;
    searchBtn.disabled = false;
    forceAnalyzeBtn.disabled = false;
}

// Update folder path input when a folder is selected
folderInput.addEventListener('change', (event) => {
    const files = event.target.files;
    if (files.length > 0) {
        // Extract the folder path from the first file's webkitRelativePath
        const folderPath = files[0].webkitRelativePath.split('/')[0];
        folderPathInput.value = folderPath;
        // Enable step 2 when folder is actually selected
        enableStep2();
    } else {
        folderPathInput.value = 'No folder selected...';
    }
});

/**
 * Handle search with optional force analyze
 * @param {boolean} forceAnalyze - Whether to force fresh analysis
 */
async function performSearch(forceAnalyze = false) {
    const folderPath = folderPathInput.value;
    const skills = searchInput.value;

    if (!folderPath) {
        alert('Please select a folder first.');
        return;
    }
    if (!skills.trim()) {
        alert('Please enter at least one skill to search for.');
        return;
    }

    try {
        const response = await parseResumesAPI(folderPath, skills, forceAnalyze);
        displayCacheStatus(response.cache_info);
        // Pass the total count from cache info to renderResumes
        const totalCount = response.cache_info ? response.cache_info.total_resumes : null;
        renderResumes(response.result, totalCount);
    } catch (error) {
        console.error('Failed to parse resumes:', error);
        loadingIndicator.classList.add('hidden');
        alert('An error occurred while searching for resumes. Please check the console.');
    }
}

/**
 * Handle "Search" button click to initiate the API call and display results.
 */
searchBtn.addEventListener('click', async () => {
    await performSearch(false);
});

/**
 * Handle "Force Analyze" button click to initiate fresh analysis.
 */
forceAnalyzeBtn.addEventListener('click', async () => {
    await performSearch(true);
});

/**
 * Allow pressing Enter in the search input to trigger a search.
 */
searchInput.addEventListener('keyup', (event) => {
    if (event.key === 'Enter') {
        performSearch(false);
    }
});

/**
 * Add an event listener to the close button in the modal
 */
detailsCloseBtn.addEventListener('click', () => {
    resumeDetailsModal.classList.add('hidden');
});

resumeDetailsModal.addEventListener('click', (event) => {
    // Close the modal if the background is clicked
    if (event.target === resumeDetailsModal) {
        resumeDetailsModal.classList.add('hidden');
    }
});

/**
 * Add event listeners for details buttons
 */
function addDetailsEventListeners() {
    const detailsBtns = document.querySelectorAll('.details-btn');
    detailsBtns.forEach((btn) => {
        btn.addEventListener('click', (event) => {
            console.log('Details button clicked:', event.target);
            // Get the resume data from the button's data attribute
            const resumeDataJson = event.target.closest('.details-btn').getAttribute('data-resume');
            try {
                const resumeData = JSON.parse(resumeDataJson.replace(/&quot;/g, '"'));
                showResumeDetails(resumeData);
            } catch (error) {
                console.error('Error parsing resume data:', error);
                alert('Unable to load resume details. Please try again.');
            }
        });
    });
}

// --- Cache Clearing Event Listeners ---

/**
 * Handle "Clear Current Cache" button click
 */
clearCurrentCacheBtn.addEventListener('click', async () => {
    if (!currentCacheKey) {
        alert('No current cache to clear. Please perform a search first.');
        return;
    }
    
    if (confirm('Are you sure you want to clear the current search cache? This will remove the cache for the current folder and query combination.')) {
        await clearCache('current', currentCacheKey);
    }
});

/**
 * Handle "Clear All Cache" button click
 */
clearAllCacheBtn.addEventListener('click', async () => {
    if (confirm('Are you sure you want to clear ALL cache? This will remove all cached data including both Gemini and Vector cache.')) {
        await clearCache('all');
    }
});