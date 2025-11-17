import { defineType, defineField } from 'sanity'

export default defineType({
  name: 'customerStory',
  title: 'Customer Story',
  type: 'document',
  fields: [
    defineField({
      name: 'companyName',
      title: 'Company Name',
      type: 'string',
      validation: (Rule) => Rule.required().max(100),
    }),
    defineField({
      name: 'slug',
      title: 'Slug',
      type: 'slug',
      options: {
        source: 'companyName',
        maxLength: 96,
      },
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'logo',
      title: 'Company Logo',
      type: 'image',
      options: {
        hotspot: true,
      },
      fields: [
        {
          name: 'alt',
          type: 'string',
          title: 'Alternative Text',
          validation: (Rule) => Rule.required(),
        },
      ],
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'description',
      title: 'Description',
      type: 'text',
      rows: 4,
      description: 'Brief description of the company and their use case',
      validation: (Rule) => Rule.max(500),
    }),
    defineField({
      name: 'industry',
      title: 'Industry',
      type: 'string',
      options: {
        list: [
          { title: 'Technology', value: 'technology' },
          { title: 'E-commerce', value: 'ecommerce' },
          { title: 'Healthcare', value: 'healthcare' },
          { title: 'Finance', value: 'finance' },
          { title: 'Education', value: 'education' },
          { title: 'Media & Entertainment', value: 'media' },
          { title: 'Retail', value: 'retail' },
          { title: 'Government', value: 'government' },
          { title: 'Other', value: 'other' },
        ],
      },
    }),
    defineField({
      name: 'testimonial',
      title: 'Testimonial',
      type: 'text',
      rows: 6,
      description: 'Customer quote or testimonial',
      validation: (Rule) => Rule.max(1000),
    }),
    defineField({
      name: 'results',
      title: 'Results',
      type: 'array',
      description: 'Key achievements and metrics',
      of: [
        {
          type: 'object',
          fields: [
            {
              name: 'metric',
              title: 'Metric',
              type: 'string',
              description: 'e.g., "50% faster deployment"',
              validation: (Rule) => Rule.required().max(100),
            },
            {
              name: 'description',
              title: 'Description',
              type: 'text',
              rows: 2,
              validation: (Rule) => Rule.max(200),
            },
          ],
          preview: {
            select: {
              title: 'metric',
              subtitle: 'description',
            },
          },
        },
      ],
    }),
    defineField({
      name: 'image',
      title: 'Featured Image',
      type: 'image',
      description: 'Hero image or screenshot',
      options: {
        hotspot: true,
      },
      fields: [
        {
          name: 'alt',
          type: 'string',
          title: 'Alternative Text',
          validation: (Rule) => Rule.required(),
        },
      ],
    }),
    defineField({
      name: 'isPublished',
      title: 'Is Published',
      type: 'boolean',
      initialValue: true,
    }),
  ],
  preview: {
    select: {
      title: 'companyName',
      subtitle: 'industry',
      media: 'logo',
    },
  },
  orderings: [
    {
      title: 'Company Name A-Z',
      name: 'companyNameAsc',
      by: [{ field: 'companyName', direction: 'asc' }],
    },
    {
      title: 'Most Recent',
      name: 'createdAtDesc',
      by: [{ field: '_createdAt', direction: 'desc' }],
    },
  ],
})
