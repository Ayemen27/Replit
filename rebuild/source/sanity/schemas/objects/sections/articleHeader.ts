import { defineType } from 'sanity'

export default defineType({
  name: 'articleHeaderSection',
  title: 'Article Header Section',
  type: 'object',
  fields: [
    {
      name: 'title',
      title: 'Article Title',
      type: 'string',
      validation: (Rule) => Rule.required().max(200),
    },
    {
      name: 'excerpt',
      title: 'Excerpt',
      type: 'text',
      rows: 3,
      description: 'Brief summary of the article',
      validation: (Rule) => Rule.max(300),
    },
    {
      name: 'author',
      title: 'Author',
      type: 'person',
    },
    {
      name: 'publishedAt',
      title: 'Published Date',
      type: 'datetime',
      validation: (Rule) => Rule.required(),
    },
    {
      name: 'coverImage',
      title: 'Cover Image',
      type: 'customImage',
    },
    {
      name: 'category',
      title: 'Category',
      type: 'string',
      options: {
        list: [
          { title: 'Product', value: 'product' },
          { title: 'Engineering', value: 'engineering' },
          { title: 'Community', value: 'community' },
          { title: 'Company', value: 'company' },
          { title: 'News', value: 'news' },
        ],
        layout: 'dropdown',
      },
    },
    {
      name: 'readTime',
      title: 'Read Time',
      type: 'number',
      description: 'Estimated reading time in minutes',
      validation: (Rule) => Rule.min(1).max(60),
    },
    {
      name: 'tags',
      title: 'Tags',
      type: 'array',
      of: [{ type: 'string' }],
      options: {
        layout: 'tags',
      },
    },
  ],
  preview: {
    select: {
      title: 'title',
      author: 'author.name',
      media: 'coverImage',
    },
    prepare({ title, author, media }) {
      return {
        title: title || 'Article Header',
        subtitle: author ? `By ${author}` : '',
        media,
      }
    },
  },
})
