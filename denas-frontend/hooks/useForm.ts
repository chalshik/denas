import { useState, useCallback } from 'react';

export function useForm<T extends object>(initial: T) {
  const [form, setForm] = useState<T>(initial);
  const handleInput = useCallback((e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target;
    let val: any = value;
    if (type === 'checkbox' && 'checked' in e.target) {
      val = (e.target as HTMLInputElement).checked;
    }
    setForm(f => ({ ...f, [name]: val }));
  }, []);
  const resetForm = useCallback(() => setForm(initial), [initial]);
  return { form, setForm, handleInput, resetForm };
} 