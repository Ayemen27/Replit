import { defineType } from 'sanity'

export default defineType({
  name: 'formField',
  title: 'Form Field',
  type: 'object',
  fields: [
    {
      name: 'fieldType',
      title: 'Field Type',
      type: 'string',
      options: {
        list: [
          { title: 'Text', value: 'text' },
          { title: 'Email', value: 'email' },
          { title: 'Phone', value: 'tel' },
          { title: 'Number', value: 'number' },
          { title: 'Textarea', value: 'textarea' },
          { title: 'Select', value: 'select' },
          { title: 'Checkbox', value: 'checkbox' },
          { title: 'Radio', value: 'radio' },
        ],
        layout: 'dropdown',
      },
      validation: (Rule) => Rule.required(),
      initialValue: 'text',
    },
    {
      name: 'label',
      title: 'Label',
      type: 'string',
      validation: (Rule) => Rule.required().max(100),
    },
    {
      name: 'name',
      title: 'Field Name',
      type: 'string',
      description: 'Unique identifier for the field (used in form submission)',
      validation: (Rule) => Rule.required().regex(/^[a-zA-Z_][a-zA-Z0-9_]*$/, {
        name: 'field name',
        invert: false,
      }).max(50),
    },
    {
      name: 'placeholder',
      title: 'Placeholder',
      type: 'string',
      validation: (Rule) => Rule.max(100),
    },
    {
      name: 'required',
      title: 'Required',
      type: 'boolean',
      initialValue: false,
    },
    {
      name: 'options',
      title: 'Options',
      type: 'array',
      description: 'Options for select, radio, or checkbox fields',
      of: [
        {
          type: 'object',
          fields: [
            {
              name: 'label',
              title: 'Label',
              type: 'string',
              validation: (Rule) => Rule.required(),
            },
            {
              name: 'value',
              title: 'Value',
              type: 'string',
              validation: (Rule) => Rule.required(),
            },
          ],
          preview: {
            select: {
              label: 'label',
              value: 'value',
            },
            prepare({ label, value }) {
              return {
                title: label,
                subtitle: value,
              }
            },
          },
        },
      ],
      hidden: ({ parent }) => !['select', 'radio', 'checkbox'].includes(parent?.fieldType),
    },
    {
      name: 'validation',
      title: 'Validation',
      type: 'object',
      fields: [
        {
          name: 'minLength',
          title: 'Minimum Length',
          type: 'number',
        },
        {
          name: 'maxLength',
          title: 'Maximum Length',
          type: 'number',
        },
        {
          name: 'pattern',
          title: 'Pattern (regex)',
          type: 'string',
          description: 'Regular expression for validation',
        },
        {
          name: 'errorMessage',
          title: 'Error Message',
          type: 'string',
          description: 'Custom error message',
        },
      ],
    },
  ],
  preview: {
    select: {
      label: 'label',
      fieldType: 'fieldType',
      required: 'required',
    },
    prepare({ label, fieldType, required }) {
      return {
        title: label || 'Form Field',
        subtitle: `${fieldType}${required ? ' (required)' : ''}`,
      }
    },
  },
})
