import { defineType } from 'sanity'

export default defineType({
  name: 'knowledgeBaseSearchSection',
  title: 'Knowledge Base Search Section',
  type: 'object',
  fields: [
    {
      name: 'heroTitle',
      title: 'Hero Title',
      type: 'string',
      validation: (Rule) => Rule.required().max(150),
    },
    {
      name: 'heroDescription',
      title: 'Hero Description',
      type: 'text',
      rows: 3,
      validation: (Rule) => Rule.max(300),
    },
    {
      name: 'searchPlaceholder',
      title: 'Search Placeholder',
      type: 'string',
      validation: (Rule) => Rule.max(100),
      initialValue: 'Search for help...',
    },
    {
      name: 'categories',
      title: 'Help Categories',
      type: 'array',
      of: [
        {
          type: 'object',
          fields: [
            {
              name: 'title',
              title: 'Category Title',
              type: 'string',
              validation: (Rule) => Rule.required().max(100),
            },
            {
              name: 'description',
              title: 'Description',
              type: 'text',
              rows: 2,
              validation: (Rule) => Rule.max(200),
            },
            {
              name: 'icon',
              title: 'Icon',
              type: 'string',
              description: 'Icon name or class',
            },
            {
              name: 'link',
              title: 'Link',
              type: 'link',
              description: 'Link to category page or article',
            },
            {
              name: 'articleCount',
              title: 'Article Count',
              type: 'number',
              description: 'Number of articles in this category (optional)',
            },
          ],
          preview: {
            select: {
              title: 'title',
              description: 'description',
            },
            prepare({ title, description }) {
              return {
                title: title || 'Category',
                subtitle: description,
              }
            },
          },
        },
      ],
      validation: (Rule) => Rule.min(1),
    },
    {
      name: 'popularArticles',
      title: 'Popular Articles',
      type: 'array',
      description: 'Featured or frequently accessed articles',
      of: [
        {
          type: 'object',
          fields: [
            {
              name: 'title',
              title: 'Article Title',
              type: 'string',
              validation: (Rule) => Rule.required().max(150),
            },
            {
              name: 'link',
              title: 'Link',
              type: 'link',
              validation: (Rule) => Rule.required(),
            },
          ],
          preview: {
            select: {
              title: 'title',
            },
          },
        },
      ],
    },
  ],
  preview: {
    select: {
      title: 'heroTitle',
      categoryCount: 'categories',
    },
    prepare({ title, categoryCount }) {
      return {
        title: title || 'Knowledge Base Search Section',
        subtitle: categoryCount ? `${categoryCount.length} categories` : 'No categories',
      }
    },
  },
})
