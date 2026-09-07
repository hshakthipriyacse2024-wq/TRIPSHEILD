import { create } from 'zustand';
import { Journey } from '@/types';
import { journeyApi, demoApi } from '@/services/api';

interface JourneyState {
  journeys: Journey[];
  currentJourney: Journey | null;
  loading: boolean;
  fetchJourneys: () => Promise<void>;
  fetchJourney: (id: string) => Promise<void>;
  createJourney: (data: any) => Promise<void>;
  loadDemoJourney: () => Promise<void>;
}

export const useJourneyStore = create<JourneyState>((set) => ({
  journeys: [],
  currentJourney: null,
  loading: false,
  fetchJourneys: async () => {
    set({ loading: true });
    try {
      const res = await journeyApi.list();
      set({ journeys: res.data, loading: false });
    } catch {
      set({ loading: false });
    }
  },
  fetchJourney: async (id: string) => {
    set({ loading: true });
    try {
      const res = await journeyApi.get(id);
      set({ currentJourney: res.data, loading: false });
    } catch {
      set({ loading: false });
    }
  },
  createJourney: async (data: any) => {
    set({ loading: true });
    try {
      const res = await journeyApi.create(data);
      set((state) => ({ journeys: [...state.journeys, res.data], loading: false }));
    } catch {
      set({ loading: false });
    }
  },
  loadDemoJourney: async () => {
    set({ loading: true });
    try {
      await demoApi.loadDemoJourney();
      const res = await journeyApi.list();
      set({ journeys: res.data, loading: false });
    } catch {
      set({ loading: false });
    }
  }
}));
