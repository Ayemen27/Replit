import { RestDataSource } from './RestDataSource';

interface SubmitFormInput {
  formType: string;
  name?: string;
  email: string;
  company?: string;
  message?: string;
  phone?: string;
  extraData?: any;
}

interface RestFormSubmission {
  id: number;
  form_type: string;
  name?: string;
  email: string;
  company?: string;
  message?: string;
  phone?: string;
  extra_data?: any;
  created_at: string;
}

interface SubmitFormResponse {
  message: string;
  submission: RestFormSubmission;
}

export class FormsDataSource extends RestDataSource {
  private transformFormSubmission(submission: RestFormSubmission) {
    return {
      id: submission.id,
      formType: submission.form_type,
      name: submission.name,
      email: submission.email,
      company: submission.company,
      message: submission.message,
      phone: submission.phone,
      extraData: submission.extra_data,
      createdAt: submission.created_at,
    };
  }

  async submitForm(input: SubmitFormInput) {
    const body = {
      form_type: input.formType,
      name: input.name,
      email: input.email,
      company: input.company,
      message: input.message,
      phone: input.phone,
      extra_data: input.extraData,
    };

    const response = await this.post<SubmitFormResponse>('/api/forms/submit', body);

    return {
      success: true,
      message: response.message,
      submission: this.transformFormSubmission(response.submission),
    };
  }
}
