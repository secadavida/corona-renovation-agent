import { Injectable, signal } from '@angular/core';

export interface RenovationProduct {
  name: string;
  price?: string;
}

export interface RenovationContext {
  space?: string;
  dimensions?: string;
  area?: number;
  budget?: number;
  products: RenovationProduct[];
  activities: string[];
}

@Injectable({ providedIn: 'root' })
export class RenovationContextService {
  readonly context = signal<RenovationContext>({ products: [], activities: [] });

  recordUserMessage(message: string): void {
    const normalized = message.toLowerCase();
    const changes: Partial<RenovationContext> = {};
    const activities: string[] = [];

    if (/bañ[oo]/.test(normalized)) {
      changes.space = 'Baño';
      activities.push('Espacio identificado: baño');
    }

    const dimensions = normalized.match(/(\d+(?:[.,]\d+)?)\s*(?:m|metros?)?\s*[x×]\s*(\d+(?:[.,]\d+)?)\s*(?:m|metros?)/);
    if (dimensions) {
      const width = Number(dimensions[1].replace(',', '.'));
      const length = Number(dimensions[2].replace(',', '.'));
      changes.dimensions = `${dimensions[1]} x ${dimensions[2]} m`;
      changes.area = width * length;
      activities.push(`Área registrada: ${width * length} m²`);
    }

    const budget = normalized.match(/presupuesto(?:\s+(?:de|es|es de))?\s*\$?\s*([\d.]+)/);
    if (budget) {
      changes.budget = Number(budget[1].replace(/\./g, ''));
      activities.push('Presupuesto registrado');
    }

    this.update(changes, activities);
  }

  recordAssistantMessage(message: string): void {
    const product = message.match(/(?:^|\n)\s*(?:[-*]\s*)?(Piso[^\n(]*|Mortero[^\n(]*|Rejilla[^\n(]*|Sanitario[^\n(]*|Lavamanos[^\n(]*|Grifer[ií]a[^\n(]*)/im);
    const price = message.match(/\$\s*([\d.]+)\s*COP/i);
    const current = this.context();
    const products = [...current.products];

    if (product) {
      const name = product[1].trim().replace(/\s+/g, ' ');
      if (!products.some((item) => item.name.toLowerCase() === name.toLowerCase())) {
        products.push({ name, price: price ? `$${price[1]} COP` : undefined });
      }
    }

    this.update({ products }, product ? ['Recomendaciones actualizadas'] : []);
  }

  private update(changes: Partial<RenovationContext>, newActivities: string[]): void {
    this.context.update((current) => ({
      ...current,
      ...changes,
      activities: [...current.activities, ...newActivities.filter((activity) => !current.activities.includes(activity))],
    }));
  }
}
