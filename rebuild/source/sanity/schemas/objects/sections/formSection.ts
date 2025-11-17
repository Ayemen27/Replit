import { defineType } from 'sanity'

export default defineType({
  name: 'formSection',
  title: 'Form Section',
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
      name: 'formId',
      title: 'Form ID',
      type: 'string',
      description: 'Unique identifier for backend form handling',
      validation: (Rule) => Rule.required().regex(/^[a-zA-Z0-9_-]+$/, {
        name: 'form ID',
        invert: false,
      }).max(50),
    },
    {
      name: 'fields',
      title: 'Form Fields',
      type: 'array',
      of: [{ type: 'formField' }],
      validation: (Rule) => Rule.min(1),
    },
    {
      name: 'submitText',
      title: 'Submit Button Text',
      type: 'string',
      validation: (Rule) => Rule.max(50),
      initialValue: 'Submit',
    },
    {
      name: 'successMessage',
      title: 'Success Message',
      type: 'text',
      rows: 2,
      description: 'Message displayed after successful submission',
      initialValue: 'Thank you! Your submission has been received.',
    },
    {
      name: 'submitAction',
      title: 'Submit Action',
      type: 'object',
      fields: [
        {
          name: 'type',
          title: 'Action Type',
          type: 'string',
          options: {
            list: [
              { title: 'API Endpoint', value: 'api' },
              { title: 'Email', value: 'email' },
              { title: 'CRM Integration', value: 'crm' },
            ],
          },
          initialValue: 'api',
        },
        {
          name: 'endpoint',
          title: 'API Endpoint',
          type: 'url',
          hidden: ({ parent }) => parent?.type !== 'api',
        },
        {
          name: 'emailTo',
          title: 'Email To',
          type: 'string',
          hidden: ({ parent }) => parent?.type !== 'email',
        },
      ],
    },
  ],
  preview: {
    select: {
      title: 'heading',
      formId: 'formId',
      fieldCount: 'fields',
    },
    prepare({ title, formId, fieldCount }) {
      return {
        title: title || formId || 'Form Section',
        subtitle: fieldCount ? `${fieldCount.length} fields` : 'No fields',
      }
    },
  },
})
