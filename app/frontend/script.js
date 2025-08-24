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
const summaryModal = document.getElementById('summary-modal');
const summaryContent = document.getElementById('summary-content');
const summaryCloseBtn = document.getElementById('summary-close-btn');
const loadingIndicator = document.getElementById('loading-indicator');
const cacheStatus = document.getElementById('cache-status');
const cacheIndicators = document.getElementById('cache-indicators');
const processingInfo = document.getElementById('processing-info');

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
            finalResponse = data.result;
            cacheInfo = data.cache_info;
        } else {
            alert('Failed to fetch results. Please try again.');
            finalResponse = [];
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred. Please try again.');
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
        `<span class="inline-block bg-blue-100 text-blue-800 text-xs font-medium mr-2 mb-2 px-2.5 py-1 rounded-full whitespace-nowrap">${skill || 'N/A'}</span>`
    ).join('');

    // Format company list, filtering out null or "null" string values
    const companiesHtml = (resume.last_3_companies || [])
        .filter(company => company && company.toLowerCase() !== 'null')
        .map(company => `<li>${company}</li>`).join('');

    return `
        <tr class="bg-white bg-opacity-50 border-b hover:bg-opacity-80 transition-colors duration-150">
            <th scope="row" class="px-6 py-4 font-medium text-gray-900 whitespace-nowrap">
                ${resume.name || '—'}
            </th>
            <td class="px-6 py-4">
                ${resume.contact_number || '—'}
            </td>
            <td class="px-6 py-4 font-bold">
                ${resume.years_of_experience || '—'}
            </td>
            <td class="px-6 py-4">
                <ul class="list-disc pl-5">
                    ${companiesHtml || '—'}
                </ul>
            </td>
            <td class="px-6 py-4">
                <div class="flex flex-wrap">
                    ${skillsHtml || '—'}
                </div>
            </td>
            <!-- <td class="px-2 py-4 text-center">
            <div class="relative group flex justify-center">
                <svg class="w-6 h-6 text-gray-400 cursor-pointer" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
                </svg>
                <div class="absolute right-full -translate-y-1/2 w-96 mb-2 w-64 hidden group-hover:block z-10">
                    <div class="bg-gray-800 text-white text-xs rounded py-2 px-3 shadow-lg">
                        ${resume.summary || 'No summary available.'}
                    </div>
                </div>
            </div>
        </td> -->
        <td class="px-2 py-4 text-center">
            <div id="summary-icon" class="relative flex justify-center">
                <svg class="w-6 h-6 text-gray-400 cursor-pointer" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
                </svg>
                <div id="summary-text" class="hidden w-0 h-0">
                    <p class="text-blue-600 text-base font-bold mb-2">${resume.name || '—'}</p>
                    <p class="text-sm">${resume.summary || 'No summary available.'}</p>
                </div>
            </div>
        </td>
        </tr>
    `;
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

    // Clear previous content
    cacheIndicators.innerHTML = '';
    processingInfo.innerHTML = '';

    // Vector cache indicator
    const vectorCacheIcon = document.createElement('div');
    vectorCacheIcon.className = `flex items-center space-x-2 px-3 py-1 rounded-full text-sm font-medium ${
        cacheInfo.vector_cache_hit 
            ? 'bg-green-100 text-green-800' 
            : 'bg-yellow-100 text-yellow-800'
    }`;
    vectorCacheIcon.innerHTML = `
        <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z"></path>
        </svg>
        <span>Vector: ${cacheInfo.vector_cache_hit ? 'Cached' : 'Fresh'}</span>
    `;
    cacheIndicators.appendChild(vectorCacheIcon);

    // Gemini cache indicator
    const geminiCacheIcon = document.createElement('div');
    geminiCacheIcon.className = `flex items-center space-x-2 px-3 py-1 rounded-full text-sm font-medium ${
        cacheInfo.gemini_cache_hit 
            ? 'bg-green-100 text-green-800' 
            : 'bg-blue-100 text-blue-800'
    }`;
    geminiCacheIcon.innerHTML = `
        <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clip-rule="evenodd"></path>
        </svg>
        <span>Gemini: ${cacheInfo.gemini_cache_hit ? 'Cached' : 'Fresh'}</span>
    `;
    cacheIndicators.appendChild(geminiCacheIcon);

    // Processing info
    let infoText = `${cacheInfo.total_resumes} resumes → ${cacheInfo.filtered_resumes} filtered`;
    if (cacheInfo.processing_time) {
        infoText += ` • ${cacheInfo.processing_time}s`;
    }
    if (cacheInfo.cache_key) {
        infoText += ` • Key: ${cacheInfo.cache_key}`;
    }
    
    processingInfo.textContent = infoText;
    cacheStatus.classList.remove('hidden');
}

/**
 * Renders a list of resumes to the table or shows a 'no results' message.
 * @param {Array<object>} resumes - An array of resume objects to display.
 */
function renderResumes(resumes) {
    resultsTbody.innerHTML = ''; // Clear previous results

    if (resumes.length === 0) {
        noResultsMessage.classList.remove('hidden');
        resultsTableContainer.classList.add('hidden');
    } else {
        noResultsMessage.classList.add('hidden');
        resultsTableContainer.classList.remove('hidden');
        const rowsHtml = resumes.map(createResumeTableRow).join('');
        resultsTbody.innerHTML = rowsHtml;
        addSummaryIconsEventListeners(); // Ensure icons have event listeners
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
    searchSection.classList.remove('hidden');
    searchInput.focus();
});

// Update folder path input when a folder is selected
folderInput.addEventListener('change', (event) => {
const files = event.target.files;
if (files.length > 0) {
    // Extract the folder path from the first file's webkitRelativePath
    const folderPath = files[0].webkitRelativePath.split('/')[0];
    folderPathInput.value = folderPath;
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
        renderResumes(response.result);
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
summaryCloseBtn.addEventListener('click', () => {
    summaryModal.classList.add('hidden');
});

summaryModal.addEventListener('click', (event) => {
    // Close the modal if the background is clicked
    if (event.target === summaryModal) {
        summaryModal.classList.add('hidden');
    }
});

/**
 * Add an event listener to the icon to pass the summary text to the modal
 */
function addSummaryIconsEventListeners() {
    const summaryIcons = document.querySelectorAll('#summary-icon svg');
    summaryIcons.forEach((icon) => {
        icon.addEventListener('click', (event) => {
            console.log('Summary icon clicked:', event.target);
            // Get the parent row and find the hidden summary text
            const summaryText = event.target.closest('td').querySelector('#summary-text').innerHTML;

            // Update the content of the separate div
            summaryContent.innerHTML = summaryText;

            // Show the modal
            summaryModal.classList.remove('hidden');
        });
    });
}