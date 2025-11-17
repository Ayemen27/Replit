import { defineType } from 'sanity'

export default defineType({
  name: 'testimonialSection',
  title: 'Testimonial Section',
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
      name: 'testimonials',
      title: 'Testimonials',
      type: 'array',
      of: [
        {
          type: 'object',
          fields: [
            {
              name: 'quote',
              title: 'Quote',
              type: 'text',
              rows: 4,
              validation: (Rule) => Rule.required().max(500),
            },
            {
              name: 'author',
              title: 'Author',
              type: 'object',
              fields: [
                {
                  name: 'name',
                  title: 'Name',
                  type: 'string',
                  validation: (Rule) => Rule.required(),
                },
                {
                  name: 'title',
                  title: 'Title/Position',
                  type: 'string',
                },
                {
                  name: 'company',
                  title: 'Company',
                  type: 'string',
                },
                {
                  name: 'image',
                  title: 'Photo',
                  type: 'customImage',
                },
              ],
            },
            {
              name: 'rating',
              title: 'Rating',
              type: 'number',
              description: 'Star rating (1-5)',
              validation: (Rule) => Rule.min(1).max(5).integer(),
            },
            {
              name: 'logo',
              title: 'Company Logo',
              type: 'customImage',
              description: 'Optional company logo',
            },
          ],
          preview: {
            select: {
              name: 'author.name',
              company: 'author.company',
              media: 'author.image',
            },
            prepare({ name, company, media }) {
              return {
                title: name || 'Testimonial',
                subtitle: company,
                media,
              }
            },
          },
        },
      ],
      validation: (Rule) => Rule.min(1).max(20),
    },
    {
      name: 'layout',
      title: 'Layout',
      type: 'string',
      options: {
        list: [
          { title: 'Grid', value: 'grid' },
          { title: 'Carousel', value: 'carousel' },
          { title: 'Single', value: 'single' },
        ],
        layout: 'radio',
      },
      initialValue: 'grid',
    },
    {
      name: 'columns',
      title: 'Columns',
      type: 'string',
      options: {
        list: [
          { title: '1 Column', value: '1' },
          { title: '2 Columns', value: '2' },
          { title: '3 Columns', value: '3' },
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
      testimonialCount: 'testimonials',
    },
    prepare({ title, testimonialCount }) {
      return {
        title: title || 'Testimonial Section',
        subtitle: testimonialCount ? `${testimonialCount.length} testimonials` : 'No testimonials',
      }
    },
  },
})
