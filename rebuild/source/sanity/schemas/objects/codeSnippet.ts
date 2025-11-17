import { defineType } from 'sanity'

export default defineType({
  name: 'codeSnippet',
  title: 'Code Snippet',
  type: 'object',
  fields: [
    {
      name: 'title',
      title: 'Title',
      type: 'string',
      description: 'Optional title for the code snippet',
    },
    {
      name: 'language',
      title: 'Language',
      type: 'string',
      options: {
        list: [
          { title: 'JavaScript', value: 'javascript' },
          { title: 'TypeScript', value: 'typescript' },
          { title: 'Python', value: 'python' },
          { title: 'Java', value: 'java' },
          { title: 'C++', value: 'cpp' },
          { title: 'C#', value: 'csharp' },
          { title: 'Go', value: 'go' },
          { title: 'Rust', value: 'rust' },
          { title: 'Ruby', value: 'ruby' },
          { title: 'PHP', value: 'php' },
          { title: 'Swift', value: 'swift' },
          { title: 'Kotlin', value: 'kotlin' },
          { title: 'HTML', value: 'html' },
          { title: 'CSS', value: 'css' },
          { title: 'SQL', value: 'sql' },
          { title: 'Shell', value: 'shell' },
          { title: 'JSON', value: 'json' },
          { title: 'YAML', value: 'yaml' },
          { title: 'Markdown', value: 'markdown' },
          { title: 'Plain Text', value: 'text' },
        ],
        layout: 'dropdown',
      },
      initialValue: 'javascript',
    },
    {
      name: 'code',
      title: 'Code',
      type: 'text',
      rows: 10,
      validation: (Rule) => Rule.required(),
    },
    {
      name: 'filename',
      title: 'Filename',
      type: 'string',
      description: 'Optional filename to display (e.g., app.js)',
    },
    {
      name: 'highlightLines',
      title: 'Highlight Lines',
      type: 'string',
      description: 'Lines to highlight (e.g., 1-3,5,7-9)',
    },
    {
      name: 'showLineNumbers',
      title: 'Show Line Numbers',
      type: 'boolean',
      initialValue: true,
    },
  ],
  preview: {
    select: {
      title: 'title',
      language: 'language',
      filename: 'filename',
    },
    prepare({ title, language, filename }) {
      return {
        title: title || filename || 'Code Snippet',
        subtitle: `Language: ${language || 'javascript'}`,
      }
    },
  },
})
