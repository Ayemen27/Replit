import { defineType } from 'sanity'

export default defineType({
  name: 'relatedContentSection',
  title: 'Related Content Section',
  type: 'object',
  fields: [
    {
      name: 'heading',
      title: 'Heading',
      type: 'string',
      validation: (Rule) => Rule.max(150),
      initialValue: 'Related Content',
    },
    {
      name: 'description',
      title: 'Description',
      type: 'text',
      rows: 2,
    },
    {
      name: 'items',
      title: 'Content Items',
      type: 'array',
      of: [{ type: 'contentReference' }],
      validation: (Rule) => Rule.min(1).max(12),
    },
    {
      name: 'layout',
      title: 'Layout',
      type: 'string',
      options: {
        list: [
          { title: 'Grid', value: 'grid' },
          { title: 'List', value: 'list' },
          { title: 'Carousel', value: 'carousel' },
        ],
        layout: 'radio',
      },
      initialValue: 'grid',
    },
    {
      name: 'maxItems',
      title: 'Max Items to Display',
      type: 'number',
      description: 'Maximum number of items to show (useful for automatic related content)',
      validation: (Rule) => Rule.min(1).max(12),
      initialValue: 3,
    },
    {
      name: 'columns',
      title: 'Columns (Grid Layout)',
      type: 'string',
      options: {
        list: [
          { title: '2 Columns', value: '2' },
          { title: '3 Columns', value: '3' },
          { title: '4 Columns', value: '4' },
        ],
        layout: 'radio',
      },
      initialValue: '3',
      hidden: ({ parent }) => parent?.layout !== 'grid',
    },
  ],
  preview: {
    select: {
      title: 'heading',
      itemCount: 'items',
    },
    prepare({ title, itemCount }) {
      return {
        title: title || 'Related Content Section',
        subtitle: itemCount ? `${itemCount.length} items` : 'No items',
      }
    },
  },
})
