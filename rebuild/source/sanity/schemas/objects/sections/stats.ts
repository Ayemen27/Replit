import { defineType } from 'sanity'

export default defineType({
  name: 'statsSection',
  title: 'Statistics Section',
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
      name: 'stats',
      title: 'Statistics',
      type: 'array',
      of: [
        {
          type: 'object',
          fields: [
            {
              name: 'value',
              title: 'Value',
              type: 'string',
              description: 'The statistic value (e.g., 10M+, 99%, $5B)',
              validation: (Rule) => Rule.required().max(30),
            },
            {
              name: 'label',
              title: 'Label',
              type: 'string',
              description: 'Description of the statistic',
              validation: (Rule) => Rule.required().max(100),
            },
            {
              name: 'icon',
              title: 'Icon',
              type: 'string',
              description: 'Optional icon name or class',
            },
          ],
          preview: {
            select: {
              value: 'value',
              label: 'label',
            },
            prepare({ value, label }) {
              return {
                title: value,
                subtitle: label,
              }
            },
          },
        },
      ],
      validation: (Rule) => Rule.min(1).max(8),
    },
    {
      name: 'layout',
      title: 'Layout',
      type: 'string',
      options: {
        list: [
          { title: 'Grid', value: 'grid' },
          { title: 'Row', value: 'row' },
        ],
        layout: 'radio',
      },
      initialValue: 'grid',
    },
    {
      name: 'backgroundColor',
      title: 'Background Color',
      type: 'string',
      options: {
        list: [
          { title: 'Default', value: 'default' },
          { title: 'Primary', value: 'primary' },
          { title: 'Secondary', value: 'secondary' },
          { title: 'Accent', value: 'accent' },
        ],
      },
      initialValue: 'default',
    },
  ],
  preview: {
    select: {
      title: 'heading',
      statCount: 'stats',
    },
    prepare({ title, statCount }) {
      return {
        title: title || 'Statistics Section',
        subtitle: statCount ? `${statCount.length} statistics` : 'No statistics',
      }
    },
  },
})
