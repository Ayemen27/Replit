import { defineType } from 'sanity'

export default defineType({
  name: 'codeEmbedSection',
  title: 'Code Embed Section',
  type: 'object',
  fields: [
    {
      name: 'title',
      title: 'Title',
      type: 'string',
      validation: (Rule) => Rule.max(150),
    },
    {
      name: 'language',
      title: 'Programming Language',
      type: 'string',
      options: {
        list: [
          { title: 'JavaScript', value: 'javascript' },
          { title: 'TypeScript', value: 'typescript' },
          { title: 'Python', value: 'python' },
          { title: 'HTML', value: 'html' },
          { title: 'CSS', value: 'css' },
          { title: 'JSON', value: 'json' },
          { title: 'Bash', value: 'bash' },
          { title: 'Java', value: 'java' },
          { title: 'C++', value: 'cpp' },
          { title: 'C#', value: 'csharp' },
          { title: 'Go', value: 'go' },
          { title: 'Rust', value: 'rust' },
          { title: 'Ruby', value: 'ruby' },
          { title: 'PHP', value: 'php' },
          { title: 'Swift', value: 'swift' },
          { title: 'Kotlin', value: 'kotlin' },
          { title: 'Other', value: 'text' },
        ],
        layout: 'dropdown',
      },
      validation: (Rule) => Rule.required(),
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
      description: 'Optional filename to display (e.g., "app.js")',
      validation: (Rule) => Rule.max(100),
    },
    {
      name: 'showLineNumbers',
      title: 'Show Line Numbers',
      type: 'boolean',
      initialValue: true,
    },
    {
      name: 'highlightLines',
      title: 'Highlight Lines',
      type: 'array',
      description: 'Line numbers to highlight (e.g., [1, 5, 10-15])',
      of: [{ type: 'string' }],
    },
    {
      name: 'replUrl',
      title: 'Repl URL',
      type: 'url',
      description: 'Optional link to the live Repl',
    },
    {
      name: 'theme',
      title: 'Theme',
      type: 'string',
      options: {
        list: [
          { title: 'VS Code Dark', value: 'vscode-dark' },
          { title: 'VS Code Light', value: 'vscode-light' },
          { title: 'GitHub Dark', value: 'github-dark' },
          { title: 'GitHub Light', value: 'github-light' },
          { title: 'Dracula', value: 'dracula' },
          { title: 'Nord', value: 'nord' },
        ],
      },
      initialValue: 'vscode-dark',
    },
  ],
  preview: {
    select: {
      title: 'title',
      filename: 'filename',
      language: 'language',
    },
    prepare({ title, filename, language }) {
      return {
        title: title || filename || 'Code Embed',
        subtitle: language,
      }
    },
  },
})
