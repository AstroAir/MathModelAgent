/**
 * 表单验证工具函数
 */

export interface ValidationRule {
	required?: boolean;
	min?: number;
	max?: number;
	minLength?: number;
	maxLength?: number;
	pattern?: RegExp;
	email?: boolean;
	url?: boolean;
	custom?: (value: unknown) => boolean | string;
	message?: string;
}

export interface ValidationResult {
	valid: boolean;
	message?: string;
}

/**
 * 验证单个字段
 */
export function validateField(
	value: unknown,
	rules: ValidationRule,
): ValidationResult {
	// 必填验证
	if (rules.required) {
		if (value === undefined || value === null || value === "") {
			return {
				valid: false,
				message: rules.message || "此字段为必填项",
			};
		}
	}

	// 如果值为空且非必填，跳过其他验证
	if (!value && !rules.required) {
		return { valid: true };
	}

	// 最小值验证
	if (rules.min !== undefined && typeof value === "number") {
		if (value < rules.min) {
			return {
				valid: false,
				message: rules.message || `值不能小于 ${rules.min}`,
			};
		}
	}

	// 最大值验证
	if (rules.max !== undefined && typeof value === "number") {
		if (value > rules.max) {
			return {
				valid: false,
				message: rules.message || `值不能大于 ${rules.max}`,
			};
		}
	}

	// 最小长度验证
	if (rules.minLength !== undefined && typeof value === "string") {
		if (value.length < rules.minLength) {
			return {
				valid: false,
				message: rules.message || `长度不能少于 ${rules.minLength} 个字符`,
			};
		}
	}

	// 最大长度验证
	if (rules.maxLength !== undefined && typeof value === "string") {
		if (value.length > rules.maxLength) {
			return {
				valid: false,
				message: rules.message || `长度不能超过 ${rules.maxLength} 个字符`,
			};
		}
	}

	// 邮箱验证
	if (rules.email && typeof value === "string") {
		const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
		if (!emailPattern.test(value)) {
			return {
				valid: false,
				message: rules.message || "请输入有效的邮箱地址",
			};
		}
	}

	// URL验证
	if (rules.url && typeof value === "string") {
		try {
			new URL(value);
		} catch {
			return {
				valid: false,
				message: rules.message || "请输入有效的URL地址",
			};
		}
	}

	// 正则表达式验证
	if (rules.pattern && typeof value === "string") {
		if (!rules.pattern.test(value)) {
			return {
				valid: false,
				message: rules.message || "格式不正确",
			};
		}
	}

	// 自定义验证
	if (rules.custom) {
		const result = rules.custom(value);
		if (typeof result === "string") {
			return {
				valid: false,
				message: result,
			};
		}
		if (!result) {
			return {
				valid: false,
				message: rules.message || "验证失败",
			};
		}
	}

	return { valid: true };
}

/**
 * 验证表单对象
 */
export function validateForm(
	data: Record<string, unknown>,
	rules: Record<string, ValidationRule>,
): Record<string, ValidationResult> {
	const results: Record<string, ValidationResult> = {};

	for (const [field, rule] of Object.entries(rules)) {
		results[field] = validateField(data[field], rule);
	}

	return results;
}

/**
 * 检查表单是否全部通过验证
 */
export function isFormValid(
	results: Record<string, ValidationResult>,
): boolean {
	return Object.values(results).every((result) => result.valid);
}

/**
 * 常用验证规则
 */
export const commonRules = {
	required: (message?: string): ValidationRule => ({
		required: true,
		message: message || "此字段为必填项",
	}),

	email: (message?: string): ValidationRule => ({
		email: true,
		message: message || "请输入有效的邮箱地址",
	}),

	url: (message?: string): ValidationRule => ({
		url: true,
		message: message || "请输入有效的URL地址",
	}),

	minLength: (length: number, message?: string): ValidationRule => ({
		minLength: length,
		message: message || `长度不能少于 ${length} 个字符`,
	}),

	maxLength: (length: number, message?: string): ValidationRule => ({
		maxLength: length,
		message: message || `长度不能超过 ${length} 个字符`,
	}),

	range: (min: number, max: number, message?: string): ValidationRule => ({
		min,
		max,
		message: message || `值必须在 ${min} 到 ${max} 之间`,
	}),

	pattern: (pattern: RegExp, message?: string): ValidationRule => ({
		pattern,
		message: message || "格式不正确",
	}),

	phone: (message?: string): ValidationRule => ({
		pattern: /^1[3-9]\d{9}$/,
		message: message || "请输入有效的手机号码",
	}),

	password: (message?: string): ValidationRule => ({
		minLength: 8,
		pattern: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d@$!%*?&]{8,}$/,
		message: message || "密码至少8位，包含大小写字母和数字",
	}),
};

/**
 * 组合多个验证规则
 */
export function combineRules(...rules: ValidationRule[]): ValidationRule {
	const combined: ValidationRule = {};
	for (const rule of rules) {
		Object.assign(combined, rule);
	}
	return combined;
}
