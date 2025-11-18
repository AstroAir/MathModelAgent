import {
	findSimilarPages,
	getWebContent,
	performWebSearch,
} from "@/apis/searchApi";
import { useWebSearch } from "@/composables/useWebSearch";
import type { SearchRequest, SearchResult } from "@/types/search";
import { SearchType } from "@/types/search";
import { beforeEach, describe, expect, it, vi } from "vitest";
import type { Mock } from "vitest";

// Mock the API functions
vi.mock("@/apis/searchApi", () => ({
	performWebSearch: vi.fn(),
	getWebContent: vi.fn(),
	findSimilarPages: vi.fn(),
	getSearchProviderStatus: vi.fn(),
	getAvailableProviders: vi.fn(),
}));

describe("useWebSearch", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	describe("performSearch", () => {
		it("should perform search and update state correctly", async () => {
			const mockResponse = {
				data: {
					results: [
						{
							title: "Test Result",
							url: "https://example.com",
							content: "Test content",
							score: 0.95,
						},
					],
					query: "test query",
					provider: "tavily",
					search_time: 1.5,
					total_results: 1,
				},
			};

			(performWebSearch as Mock).mockResolvedValue(mockResponse);

			const { performSearch, searchState } = useWebSearch();

			const searchRequest: SearchRequest = {
				query: "test query",
				search_type: SearchType.GENERAL,
				max_results: 10,
			};

			const results = await performSearch(searchRequest);

			expect(performWebSearch).toHaveBeenCalledWith(searchRequest);
			expect(results).toEqual(mockResponse.data.results);
			expect(searchState.results).toEqual(mockResponse.data.results);
			expect(searchState.lastQuery).toBe("test query");
			expect(searchState.searchTime).toBe(1.5);
			expect(searchState.totalResults).toBe(1);
			expect(searchState.isLoading).toBe(false);
			expect(searchState.error).toBeNull();
		});

		it("should handle search errors correctly", async () => {
			const mockError = {
				response: {
					data: {
						detail: {
							message: "Search failed",
						},
					},
				},
			};

			(performWebSearch as Mock).mockRejectedValue(mockError);

			const { performSearch, searchState } = useWebSearch();

			const searchRequest: SearchRequest = {
				query: "test query",
				search_type: SearchType.GENERAL,
			};

			await expect(performSearch(searchRequest)).rejects.toThrow(
				"Search failed",
			);
			expect(searchState.error).toBe("Search failed");
			expect(searchState.isLoading).toBe(false);
		});
	});

	describe("getContentForUrl", () => {
		it("should retrieve content for a single URL", async () => {
			const mockResponse = {
				data: {
					"https://example.com": "Page content",
				},
			};

			(getWebContent as Mock).mockResolvedValue(mockResponse);

			const { getContentForUrl } = useWebSearch();
			const content = await getContentForUrl("https://example.com");

			expect(getWebContent).toHaveBeenCalledWith(["https://example.com"]);
			expect(content).toBe("Page content");
		});

		it("should return null when content retrieval fails", async () => {
			(getWebContent as Mock).mockRejectedValue(
				new Error("Failed to get content"),
			);

			const { getContentForUrl } = useWebSearch();
			const content = await getContentForUrl("https://example.com");

			expect(content).toBeNull();
		});
	});

	describe("getContentForUrls", () => {
		it("should retrieve content for multiple URLs", async () => {
			const mockResponse = {
				data: {
					"https://example.com": "Content 1",
					"https://test.com": "Content 2",
				},
			};

			(getWebContent as Mock).mockResolvedValue(mockResponse);

			const { getContentForUrls } = useWebSearch();
			const content = await getContentForUrls([
				"https://example.com",
				"https://test.com",
			]);

			expect(getWebContent).toHaveBeenCalledWith([
				"https://example.com",
				"https://test.com",
			]);
			expect(content).toEqual(mockResponse.data);
		});
	});

	describe("findSimilar", () => {
		it("should find similar pages", async () => {
			const mockResponse = {
				data: [
					{
						title: "Similar Page",
						url: "https://similar.com",
						content: "Similar content",
					},
				],
			};

			(findSimilarPages as Mock).mockResolvedValue(mockResponse);

			const { findSimilar } = useWebSearch();
			const results = await findSimilar("https://example.com", 5);

			expect(findSimilarPages).toHaveBeenCalledWith("https://example.com", 5);
			expect(results).toEqual(mockResponse.data);
		});
	});

	describe("quick search methods", () => {
		it("should perform general search", async () => {
			const mockResponse = {
				data: {
					results: [],
					query: "test",
					provider: "tavily",
					search_time: 1.0,
					total_results: 0,
				},
			};

			(performWebSearch as Mock).mockResolvedValue(mockResponse);

			const { searchGeneral } = useWebSearch();
			await searchGeneral("test", 5);

			expect(performWebSearch).toHaveBeenCalledWith({
				query: "test",
				search_type: "general",
				max_results: 5,
				include_content: true,
			});
		});

		it("should perform academic search", async () => {
			const mockResponse = {
				data: {
					results: [],
					query: "research",
					provider: "exa",
					search_time: 2.0,
					total_results: 0,
				},
			};

			(performWebSearch as Mock).mockResolvedValue(mockResponse);

			const { searchAcademic } = useWebSearch();
			await searchAcademic("research", 8);

			expect(performWebSearch).toHaveBeenCalledWith({
				query: "research",
				search_type: "academic",
				max_results: 8,
				include_content: true,
			});
		});

		it("should perform code search", async () => {
			const mockResponse = {
				data: {
					results: [],
					query: "python function",
					provider: "tavily",
					search_time: 1.2,
					total_results: 0,
				},
			};

			(performWebSearch as Mock).mockResolvedValue(mockResponse);

			const { searchCode } = useWebSearch();
			await searchCode("python function");

			expect(performWebSearch).toHaveBeenCalledWith({
				query: "python function",
				search_type: "code",
				max_results: 10,
				include_content: true,
			});
		});
	});

	describe("utility methods", () => {
		it("should format search results correctly", () => {
			const { formatSearchResults } = useWebSearch();

			const results: SearchResult[] = [
				{
					title: "Test Result 1",
					url: "https://example1.com",
					content:
						"This is a test content that is longer than 200 characters and should be truncated to show only the first 200 characters followed by ellipsis to indicate that there is more content available.",
				},
				{
					title: "Test Result 2",
					url: "https://example2.com",
					content: "Short content",
				},
			];

			const formatted = formatSearchResults(results);

			expect(formatted).toContain("1. Test Result 1");
			expect(formatted).toContain("2. Test Result 2");
			expect(formatted).toContain("https://example1.com");
			expect(formatted).toContain("https://example2.com");
			expect(formatted).toContain("...");
		});

		it("should handle empty results", () => {
			const { formatSearchResults } = useWebSearch();
			const formatted = formatSearchResults([]);
			expect(formatted).toBe("No results found.");
		});

		it("should filter results by domain", () => {
			const { getResultsByDomain, searchState } = useWebSearch();

			// Mock search state with results
			searchState.results = [
				{ title: "Result 1", url: "https://github.com/test" },
				{ title: "Result 2", url: "https://stackoverflow.com/test" },
				{ title: "Result 3", url: "https://github.com/another" },
			] as SearchResult[];

			const githubResults = getResultsByDomain("github.com");
			expect(githubResults).toHaveLength(2);
			expect(githubResults[0].title).toBe("Result 1");
			expect(githubResults[1].title).toBe("Result 3");
		});

		it("should filter high-scored results", () => {
			const { getHighScoredResults, searchState } = useWebSearch();

			searchState.results = [
				{ title: "High Score", url: "https://example.com", score: 0.95 },
				{ title: "Low Score", url: "https://example.com", score: 0.5 },
				{ title: "Medium Score", url: "https://example.com", score: 0.75 },
				{ title: "Very High Score", url: "https://example.com", score: 0.98 },
			] as SearchResult[];

			const highScored = getHighScoredResults(0.8);
			expect(highScored).toHaveLength(2);
			expect(highScored[0].title).toBe("High Score");
			expect(highScored[1].title).toBe("Very High Score");
		});
	});

	describe("state management", () => {
		it("should clear results correctly", () => {
			const { clearResults, searchState } = useWebSearch();

			// Set some state
			searchState.results = [
				{ title: "Test", url: "https://example.com" },
			] as SearchResult[];
			searchState.lastQuery = "test query";
			searchState.error = "Some error";
			searchState.searchTime = 1.5;
			searchState.totalResults = 1;

			clearResults();

			expect(searchState.results).toEqual([]);
			expect(searchState.lastQuery).toBe("");
			expect(searchState.error).toBeNull();
			expect(searchState.searchTime).toBe(0);
			expect(searchState.totalResults).toBe(0);
		});

		it("should clear error correctly", () => {
			const { clearError, searchState } = useWebSearch();

			searchState.error = "Some error";
			clearError();

			expect(searchState.error).toBeNull();
		});
	});
});
