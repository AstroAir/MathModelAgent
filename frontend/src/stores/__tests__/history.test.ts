/**
 * History Store Unit Tests
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useHistoryStore } from '../history'
import type { TaskHistoryItem } from '@/types/history'

// Mock the API module
vi.mock('@/apis/historyApi', () => ({
  getTaskHistoryList: vi.fn(),
  getTaskHistory: vi.fn(),
  createTaskHistory: vi.fn(),
  updateTaskHistory: vi.fn(),
  toggleTaskPin: vi.fn(),
  deleteTaskHistory: vi.fn(),
  getTaskCount: vi.fn(),
}))

describe('History Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('initializes with correct default state', () => {
    const store = useHistoryStore()

    expect(store.tasks).toEqual([])
    expect(store.loading).toBe(false)
    expect(store.error).toBe(null)
    expect(store.total).toBe(0)
    expect(store.taskCount).toEqual({
      total: 0,
      custom: 0,
      example: 0,
    })
    expect(store.pagination).toEqual({
      currentPage: 1,
      itemsPerPage: 20,
      totalPages: 1,
    })
  })

  it('filters tasks correctly', () => {
    const store = useHistoryStore()
    const mockTasks: TaskHistoryItem[] = [
      {
        task_id: '1',
        title: 'Test Task 1',
        description: 'Description 1',
        task_type: 'custom',
        is_pinned: true,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
        status: 'completed',
        file_count: 1,
      },
      {
        task_id: '2',
        title: 'Test Task 2',
        description: 'Description 2',
        task_type: 'example',
        is_pinned: false,
        created_at: '2024-01-02T00:00:00Z',
        updated_at: '2024-01-02T00:00:00Z',
        status: 'processing',
        file_count: 2,
      },
    ]

    store.tasks = mockTasks

    // Test pinned tasks
    expect(store.pinnedTasks).toHaveLength(1)
    expect(store.pinnedTasks[0].task_id).toBe('1')

    // Test custom tasks
    expect(store.customTasks).toHaveLength(1)
    expect(store.customTasks[0].task_id).toBe('1')

    // Test example tasks
    expect(store.exampleTasks).toHaveLength(1)
    expect(store.exampleTasks[0].task_id).toBe('2')
  })

  it('handles search filtering correctly', () => {
    const store = useHistoryStore()
    const mockTasks: TaskHistoryItem[] = [
      {
        task_id: '1',
        title: 'Linear Regression',
        description: 'Machine learning model',
        task_type: 'custom',
        is_pinned: false,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
        status: 'completed',
        file_count: 1,
      },
      {
        task_id: '2',
        title: 'Neural Network',
        description: 'Deep learning project',
        task_type: 'custom',
        is_pinned: false,
        created_at: '2024-01-02T00:00:00Z',
        updated_at: '2024-01-02T00:00:00Z',
        status: 'completed',
        file_count: 2,
      },
    ]

    store.tasks = mockTasks
    store.setSearchFilter('regression')

    expect(store.filteredTasks).toHaveLength(1)
    expect(store.filteredTasks[0].title).toBe('Linear Regression')
  })

  it('handles pagination correctly', () => {
    const store = useHistoryStore()
    const mockTasks: TaskHistoryItem[] = Array.from({ length: 25 }, (_, i) => ({
      task_id: `task_${i + 1}`,
      title: `Task ${i + 1}`,
      description: `Description ${i + 1}`,
      task_type: 'custom',
      is_pinned: false,
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
      status: 'completed',
      file_count: 1,
    }))

    store.tasks = mockTasks

    // Test first page
    expect(store.paginatedTasks).toHaveLength(20)
    expect(store.pagination.totalPages).toBe(2)

    // Test second page
    store.setCurrentPage(2)
    expect(store.paginatedTasks).toHaveLength(5)
  })

  it('resets pagination when changing page size', () => {
    const store = useHistoryStore()

    store.setCurrentPage(3)
    expect(store.pagination.currentPage).toBe(3)

    store.setItemsPerPage(50)
    expect(store.pagination.currentPage).toBe(1)
    expect(store.pagination.itemsPerPage).toBe(50)
  })

  it('resets pagination when searching', () => {
    const store = useHistoryStore()

    store.setCurrentPage(3)
    expect(store.pagination.currentPage).toBe(3)

    store.setSearchFilter('test')
    expect(store.pagination.currentPage).toBe(1)
  })

  it('resets state correctly', () => {
    const store = useHistoryStore()

    // Set some state
    store.tasks = [
      {
        task_id: '1',
        title: 'Test',
        description: 'Test',
        task_type: 'custom',
        is_pinned: false,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
        status: 'completed',
        file_count: 1,
      },
    ]
    store.loading = true
    store.error = 'Test error'
    store.total = 10
    store.setCurrentPage(2)
    store.setSearchFilter('test')

    // Reset
    store.reset()

    // Check reset state
    expect(store.tasks).toEqual([])
    expect(store.loading).toBe(false)
    expect(store.error).toBe(null)
    expect(store.total).toBe(0)
    expect(store.pagination.currentPage).toBe(1)
    expect(store.pagination.itemsPerPage).toBe(20)
    expect(store.currentFilter.search).toBeUndefined()
  })
})
