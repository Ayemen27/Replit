import { defineType } from 'sanity'

export default defineType({
  name: 'faqSection',
  title: 'FAQ Section',
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
      name: 'faqs',
      title: 'FAQs',
      type: 'array',
      of: [
        {
          type: 'object',
          fields: [
            {
              name: 'question',
              title: 'Question',
              type: 'string',
              validation: (Rule) => Rule.required().max(200),
            },
            {
              name: 'answer',
              title: 'Answer',
              type: 'richText',
              validation: (Rule) => Rule.required(),
            },
            {
              name: 'category',
              title: 'Category',
              type: 'string',
              description: 'Optional category for grouping FAQs',
            },
          ],
          preview: {
            select: {
              title: 'question',
              category: 'category',
            },
            prepare({ title, category }) {
              return {
                title,
                subtitle: category || 'Uncategorized',
              }
            },
          },
        },
      ],
      validation: (Rule) => Rule.min(1).max(50),
    },
    {
      name: 'layout',
      title: 'Layout',
      type: 'string',
      options: {
        list: [
          { title: 'Accordion', value: 'accordion' },
          { title: 'Two Column', value: 'two-column' },
        ],
        layout: 'radio',
      },
      initialValue: 'accordion',
    },
    {
      name: 'defaultExpanded',
      title: 'Default Expanded',
      type: 'boolean',
      description: 'Expand all FAQs by default',
      initialValue: false,
    },
  ],
  preview: {
    select: {
      title: 'heading',
      faqCount: 'faqs',
    },
    prepare({ title, faqCount }) {
      return {
        title: title || 'FAQ Section',
        subtitle: faqCount ? `${faqCount.length} questions` : 'No questions',
      }
    },
  },
})
