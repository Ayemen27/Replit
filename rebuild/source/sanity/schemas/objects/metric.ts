import { defineType } from 'sanity'

export default defineType({
  name: 'metric',
  title: 'Metric',
  type: 'object',
  fields: [
    {
      name: 'label',
      title: 'Label',
      type: 'string',
      description: 'Description of the metric',
      validation: (Rule) => Rule.required().max(100),
    },
    {
      name: 'value',
      title: 'Value',
      type: 'string',
      description: 'The metric value (e.g., 10M+, 99%, $5B)',
      validation: (Rule) => Rule.required().max(30),
    },
    {
      name: 'unit',
      title: 'Unit',
      type: 'string',
      description: 'Unit of measurement (optional, e.g., users, %, $)',
      validation: (Rule) => Rule.max(20),
    },
    {
      name: 'icon',
      title: 'Icon',
      type: 'string',
      description: 'Optional icon name or class',
    },
    {
      name: 'change',
      title: 'Change Percentage',
      type: 'object',
      description: 'Optional growth/change indicator',
      fields: [
        {
          name: 'value',
          title: 'Change Value',
          type: 'number',
          description: 'Percentage change (positive or negative)',
        },
        {
          name: 'period',
          title: 'Period',
          type: 'string',
          description: 'Time period for the change (e.g., "vs last month")',
          validation: (Rule) => Rule.max(50),
        },
      ],
    },
  ],
  preview: {
    select: {
      value: 'value',
      label: 'label',
      unit: 'unit',
    },
    prepare({ value, label, unit }) {
      return {
        title: `${value}${unit ? ` ${unit}` : ''}`,
        subtitle: label,
      }
    },
  },
})
