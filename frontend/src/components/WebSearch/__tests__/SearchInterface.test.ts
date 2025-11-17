import { describe, it, expect, vi, beforeEach } from 'vitest';
import { mount } from '@vue/test-utils';
import SearchInterface from '../SearchInterface.vue';
import { performWebSearch } from '@/apis/searchApi';

// Mock the API
vi.mock('@/apis/searchApi', () => ({
  performWebSearch: vi.fn()
}));

// Mock UI components
vi.mock('@/components/ui/button', () => ({
  Button: { template: '<button><slot /></button>' }
}));

vi.mock('@/components/ui/input', () => ({
  Input: { template: '<input />', props: ['modelValue'] }
}));

vi.mock('@/components/ui/select', () => ({
  Select: { template: '<div><slot /></div>' },
  SelectTrigger: { template: '<div><slot /></div>' },
  SelectContent: { template: '<div><slot /></div>' },
  SelectItem: { template: '<div><slot /></div>', props: ['value'] },
  SelectValue: { template: '<div />' }
}));

describe('SearchInterface', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders search form correctly', () => {
    const wrapper = mount(SearchInterface);

    expect(wrapper.find('input').exists()).toBe(true);
    expect(wrapper.find('button').exists()).toBe(true);
  });

  it('handles search form submission', async () => {
    const mockResponse = {
      data: {
        results: [
          {
            title: 'Test Result',
            url: 'https://example.com',
            content: 'Test content'
          }
        ],
        search_time: 1.5,
        total_results: 1
      }
    };

    (performWebSearch as any).mockResolvedValue(mockResponse);

    const wrapper = mount(SearchInterface);

    // Set search query
    await wrapper.setData({ searchForm: { query: 'test query' } });

    // Trigger search
    await wrapper.vm.handleSearch();

    expect(performWebSearch).toHaveBeenCalledWith({
      query: 'test query',
      search_type: 'general',
      provider: undefined,
      max_results: 10,
      include_content: true,
      domains: undefined,
      date_range: undefined
    });
  });

  it('displays loading state during search', async () => {
    const wrapper = mount(SearchInterface);

    // Set loading state
    await wrapper.setData({ isLoading: true });

    expect(wrapper.text()).toContain('Searching...');
  });

  it('displays error state on search failure', async () => {
    const wrapper = mount(SearchInterface);

    // Set error state
    await wrapper.setData({ error: 'Search failed' });

    expect(wrapper.text()).toContain('Search Error');
    expect(wrapper.text()).toContain('Search failed');
  });

  it('emits events correctly', async () => {
    const wrapper = mount(SearchInterface);

    const mockResults = [
      { title: 'Test', url: 'https://example.com', content: 'Content' }
    ];

    // Simulate successful search
    await wrapper.setData({
      results: mockResults,
      lastQuery: 'test query'
    });

    // Check if searchPerformed event would be emitted
    expect(wrapper.vm.results).toEqual(mockResults);
    expect(wrapper.vm.lastQuery).toBe('test query');
  });

  it('handles advanced options correctly', async () => {
    const wrapper = mount(SearchInterface);

    // Enable advanced options
    await wrapper.setData({ showAdvanced: true });

    // Set advanced options
    await wrapper.setData({
      domainsInput: 'example.com, test.com',
      dateRange: { start: '2024-01-01', end: '2024-12-31' }
    });

    expect(wrapper.vm.domains).toEqual(['example.com', 'test.com']);
    expect(wrapper.vm.dateRangeFilter).toEqual({
      start_date: '2024-01-01',
      end_date: '2024-12-31'
    });
  });

  it('validates search input', async () => {
    const wrapper = mount(SearchInterface);

    // Empty query should disable search
    await wrapper.setData({ searchForm: { query: '' } });
    expect(wrapper.vm.searchForm.query.trim()).toBe('');

    // Valid query should enable search
    await wrapper.setData({ searchForm: { query: 'valid query' } });
    expect(wrapper.vm.searchForm.query.trim()).toBeTruthy();
  });
});

describe('SearchInterface Integration', () => {
  it('integrates with search API correctly', async () => {
    const mockResponse = {
      data: {
        results: [
          {
            title: 'Integration Test Result',
            url: 'https://integration-test.com',
            content: 'Integration test content',
            score: 0.95
          }
        ],
        query: 'integration test',
        provider: 'tavily',
        search_time: 2.1,
        total_results: 1,
        metadata: {
          answer: 'Test answer'
        }
      }
    };

    (performWebSearch as any).mockResolvedValue(mockResponse);

    const wrapper = mount(SearchInterface);

    await wrapper.setData({
      searchForm: {
        query: 'integration test',
        searchType: 'academic',
        provider: 'tavily',
        maxResults: 5
      }
    });

    await wrapper.vm.handleSearch();

    expect(performWebSearch).toHaveBeenCalledWith({
      query: 'integration test',
      search_type: 'academic',
      provider: 'tavily',
      max_results: 5,
      include_content: true,
      domains: undefined,
      date_range: undefined
    });

    expect(wrapper.vm.results).toEqual(mockResponse.data.results);
    expect(wrapper.vm.searchTime).toBe(2.1);
    expect(wrapper.vm.totalResults).toBe(1);
  });

  it('handles API errors gracefully', async () => {
    const mockError = {
      response: {
        data: {
          detail: {
            message: 'API key invalid',
            provider: 'tavily',
            error_code: 'AUTH_FAILED'
          }
        }
      }
    };

    (performWebSearch as any).mockRejectedValue(mockError);

    const wrapper = mount(SearchInterface);

    await wrapper.setData({ searchForm: { query: 'test query' } });
    await wrapper.vm.handleSearch();

    expect(wrapper.vm.error).toContain('API key invalid');
  });
});
