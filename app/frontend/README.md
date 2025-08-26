# AI-powered Resume Parser - React Frontend

A modern React TypeScript frontend for the AI-powered Resume Parser application built with Vite and Tailwind CSS.

## Features

- **Modern React TypeScript**: Built with React 18 and TypeScript for type safety
- **Vite**: Fast build tool and dev server
- **Tailwind CSS**: Utility-first CSS framework for rapid UI development
- **Lucide React**: Beautiful, customizable icons
- **Responsive Design**: Works on desktop and mobile devices
- **Dark Theme**: GitHub-inspired dark mode design

## Components

- **Header**: Application header with resume count display
- **FolderSelection**: Step 1 - Folder path input and selection
- **SearchSkills**: Step 2 - Skills search with force analyze option
- **CacheStatus**: Cache status indicators and cache management
- **LoadingIndicator**: Loading spinner during API calls
- **ResumeTable**: Results table with sortable resume data
- **ResumeDetailsModal**: Detailed view of individual resumes

## Getting Started

### Prerequisites

- Node.js (v16 or higher)
- npm or yarn

### Installation

1. Navigate to the frontend directory:
   ```bash
   cd app/frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

4. Open your browser and go to `http://localhost:3000`

### Building for Production

```bash
npm run build
```

The build artifacts will be stored in the `dist/` directory.

### Preview Production Build

```bash
npm run preview
```

## API Integration

The frontend communicates with the Python backend API running on `http://localhost:8000`. Make sure the backend server is running before using the application.

### API Endpoints

- `POST /parse-resume`: Parse resumes from a folder
- `POST /clear-cache`: Clear cache (current or all)

## Project Structure

```
src/
├── components/          # React components
│   ├── Header.tsx
│   ├── FolderSelection.tsx
│   ├── SearchSkills.tsx
│   ├── CacheStatus.tsx
│   ├── LoadingIndicator.tsx
│   ├── ResumeTable.tsx
│   └── ResumeDetailsModal.tsx
├── services/           # API service layer
│   └── api.ts
├── types/             # TypeScript type definitions
│   └── index.ts
├── utils/             # Utility functions
│   └── resume.ts
├── App.tsx            # Main application component
├── main.tsx          # Application entry point
└── index.css         # Global styles
```

## Features Overview

### Step-by-Step Workflow

1. **Folder Selection**: Enter or browse for the resume folder path
2. **Skills Search**: Enter skills to search for and execute the search
3. **Results Display**: View matching resumes in a sortable table
4. **Detailed View**: Click on any resume to see detailed information

### Advanced Features

- **Cache Management**: View cache status and clear cache when needed
- **Force Analysis**: Bypass cache for fresh analysis
- **Score-based Sorting**: Resumes are automatically sorted by match score
- **Responsive Design**: Works seamlessly on all device sizes

## Technologies Used

- **React 18**: Modern React with hooks
- **TypeScript**: Type-safe JavaScript
- **Vite**: Next-generation frontend tooling
- **Tailwind CSS**: Utility-first CSS framework
- **Lucide React**: Beautiful icon library
- **PostCSS**: CSS post-processing
- **ESLint**: Code linting and formatting

## Browser Support

This application supports all modern browsers including:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Development

### Available Scripts

- `npm run dev`: Start development server
- `npm run build`: Build for production
- `npm run preview`: Preview production build
- `npm run lint`: Run ESLint

### Code Style

The project uses ESLint and TypeScript for code quality and consistency. Make sure to run the linter before committing changes.

## Contributing

1. Follow the existing code style and patterns
2. Add TypeScript types for all new components and functions
3. Test your changes thoroughly
4. Update documentation as needed

## License

This project is part of the AI-powered Resume Parser application.
