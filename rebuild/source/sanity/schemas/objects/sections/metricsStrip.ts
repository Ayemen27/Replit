import { defineType } from 'sanity'

export default defineType({
  name: 'metricsStripSection',
  title: 'Metrics Strip Section',
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
      name: 'metrics',
      title: 'Metrics',
      type: 'array',
      of: [{ type: 'metric' }],
      validation: (Rule) => Rule.min(1).max(6),
    },
    {
      name: 'layout',
      title: 'Layout',
      type: 'string',
      options: {
        list: [
          { title: 'Horizontal', value: 'horizontal' },
          { title: 'Vertical', value: 'vertical' },
        ],
        layout: 'radio',
      },
      initialValue: 'horizontal',
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
      metricCount: 'metrics',
    },
    prepare({ title, metricCount }) {
      return {
        title: title || 'Metrics Strip Section',
        subtitle: metricCount ? `${metricCount.length} metrics` : 'No metrics',
      }
    },
  },
})
