 // --- DOM Elements ---
 const browseBtn = document.getElementById('browse-btn');
 const folderPathInput = document.getElementById('folder-path');
 const folderInput = document.getElementById('folder-input');
 const searchInput = document.getElementById('search-input');
 const searchBtn = document.getElementById('search-btn');
 const resultsTableContainer = document.getElementById('results-table-container');
 const resultsTbody = document.getElementById('results-tbody');
 const noResultsMessage = document.getElementById('no-results');
 const searchSection = document.getElementById('search-section');
 const loadingIndicator = document.getElementById('loading-indicator');

 // --- Functions ---

  /**
  * In a real application, this would be a fetch() call to your Python server.
  * @param {string} folderPath - The path of the folder to search.
  * @param {string} skills - Comma-separated skills to search for.
  * @returns {Promise<Array<object>>} - A promise that resolves with the parsed data.
  */
  async function parseResumesAPI(folderPath, skills) {
     console.log(`API Call: Parsing resumes from '${folderPath}' for skills: '${skills}'`);
     
     // Show the loader while the API call is in progress
     loadingIndicator.classList.remove('hidden');
     resultsTableContainer.classList.add('hidden');
     noResultsMessage.classList.add('hidden');

     let finalResponse = [];

     try {
         const response = await fetch('http://localhost:8000/parse-resume', {
             method: 'POST',
             headers: {
                 'Content-Type': 'application/json',
             },
             body: JSON.stringify({
                 dirPath: folderPath,
                 query: skills,
             }),
         });

         if (response.ok) {
             const data = await response.json();
             // Simulate filtering based on skills for a more realistic demo
             const skillList = skills.toLowerCase().split(',').map(s => s.trim()).filter(Boolean);
             const filteredResponse = skillList.length === 0 ? data.result : data.result.filter(resume => 
                 resume.top_5_technical_skills.some(skill => 
                     skillList.includes(skill.toLowerCase())
                 )
             );
             finalResponse = filteredResponse;
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
     return finalResponse;
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
             <td class="px-2 py-4 text-center">
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
            </td>
         </tr>
     `;
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
  * Handle "Search" button click to initiate the API call and display results.
  */
 searchBtn.addEventListener('click', async () => {
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
         // const resumeData = await parseResumesAPIMock(folderPath, skills);
         const resumeData = await parseResumesAPI(folderPath, skills);
         renderResumes(resumeData);
     } catch (error) {
         console.error('Failed to parse resumes:', error);
         loadingIndicator.classList.add('hidden');
         alert('An error occurred while searching for resumes. Please check the console.');
     }
 });

 /**
  * Allow pressing Enter in the search input to trigger a search.
  */
 searchInput.addEventListener('keyup', (event) => {
     if (event.key === 'Enter') {
         searchBtn.click();
     }
 });