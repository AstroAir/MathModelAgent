// Response types for the application
export interface Message {
	id: string;
	type: string;
	content: string;
	timestamp: number;
	sender?: string;
	msg_type?: string;
	agent_type?: string;
	step_name?: string;
	status?: string;
	tool_name?: string;
	step_type?: string;
	details?: Record<string, unknown>;
}

export interface UserMessage extends Message {
	type: "user";
}

export interface StepMessage {
	id: string;
	step: string;
	status: "processing" | "completed" | "failed";
	content: string;
	timestamp: number;
	step_name?: string;
	agent_type?: string;
	step_type?: string;
	details?: Record<string, unknown>;
}

export interface CoordinatorMessage extends Message {
	type: "coordinator";
}

export interface ModelerMessage extends Message {
	type: "modeler";
}

export interface CoderMessage extends Message {
	type: "coder";
}

export interface WriterMessage extends Message {
	type: "writer";
	sub_title?: string;
}

export interface InterpreterMessage extends Message {
	type: "interpreter";
}

export interface CodeExecutionResult {
	success: boolean;
	output?: string;
	error?: string;
	execution_time?: number;
	res_type?: string;
	format?: string;
	msg?: string | null;
	name?: string;
	value?: string;
	traceback?: string;
}

export interface OutputItem {
	res_type: string;
	format?: string;
	msg?: string | null;
	name?: string;
	value?: string;
	traceback?: string;
}

export interface FileContentResponse {
	content: string;
	filename: string;
	file_type?: string;
	is_image?: boolean;
	mime_type?: string;
	size?: number;
	encoding?: string;
	truncated?: boolean;
}
