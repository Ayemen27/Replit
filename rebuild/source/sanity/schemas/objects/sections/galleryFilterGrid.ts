import { defineType } from 'sanity'

export default defineType({
  name: 'galleryFilterGridSection',
  title: 'Gallery Filter Grid Section',
  type: 'object',
  fields: [
    {
      name: 'heading',
      title: 'Heading',
      type: 'string',
      validation: (Rule) => Rule.max(150),
    },
    {
      name: 'description',
      title: 'Description',
      type: 'text',
      rows: 3,
    },
    {
      name: 'categories',
      title: 'Filter Categories',
      type: 'array',
      of: [
        {
          type: 'object',
          fields: [
            {
              name: 'name',
              title: 'Category Name',
              type: 'string',
              validation: (Rule) => Rule.required().max(100),
            },
            {
              name: 'slug',
              title: 'Slug',
              type: 'slug',
              description: 'URL-friendly version of the category name',
              options: {
                source: 'name',
              },
              validation: (Rule) => Rule.required(),
            },
            {
              name: 'count',
              title: 'Item Count',
              type: 'number',
              description: 'Number of items in this category (optional, can be computed)',
            },
            {
              name: 'icon',
              title: 'Icon',
              type: 'string',
              description: 'Icon name or class',
            },
          ],
          preview: {
            select: {
              name: 'name',
              count: 'count',
            },
            prepare({ name, count }) {
              return {
                title: name || 'Category',
                subtitle: count ? `${count} items` : '',
              }
            },
          },
        },
      ],
    },
    {
      name: 'defaultView',
      title: 'Default View',
      type: 'string',
      options: {
        list: [
          { title: 'Grid', value: 'grid' },
          { title: 'List', value: 'list' },
        ],
        layout: 'radio',
      },
      initialValue: 'grid',
    },
    {
      name: 'itemsPerPage',
      title: 'Items Per Page',
      type: 'number',
      description: 'Number of items to display per page',
      validation: (Rule) => Rule.min(6).max(100),
      initialValue: 12,
    },
    {
      name: 'enableSearch',
      title: 'Enable Search',
      type: 'boolean',
      description: 'Show search bar for filtering items',
      initialValue: true,
    },
  ],
  preview: {
    select: {
      title: 'heading',
      categoryCount: 'categories',
    },
    prepare({ title, categoryCount }) {
      return {
        title: title || 'Gallery Filter Grid Section',
        subtitle: categoryCount ? `${categoryCount.length} categories` : 'No categories',
      }
    },
  },
})
