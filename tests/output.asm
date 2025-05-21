section .data
	list1_a dq 5, 7
	list2_a dq 0, 5
	concat_list_a dq 5, 7, 0, 5
	concat_list_a_len dq 4
	open_bracket_a db "["
	comma_space db ", "
	close_bracket_a db "]"
	newline db 0xA
	minus_sign db "-"

section .bss
	buffer resb 20


section .text
	global _start
	global fn
	global f


;	---print_rax protocol---
print_rax:
	test rax, rax
	jns .positive
	push rax
	mov rax, 1
	mov rdi, 1
	mov rsi, minus_sign
	mov rdx, 1
	syscall
	pop rax
	neg rax
.positive:
	mov rcx, buffer + 20
	mov rbx, 10

.convert_loop:
	xor rdx, rdx
	div rbx
	add dl, '0'
	dec rcx
	mov [rcx], dl
	test rax, rax
	jnz .convert_loop

	; write result
	mov rax, 1
	mov rdi, 1
	mov rsi, rcx
	mov rdx, buffer + 20
	sub rdx, rcx
	syscall
	ret
;	--------------------

; ---print_str protocol---
print_str:
	xor rcx, rcx

.find_len_str:
	mov al, [rsi + rcx]
	test al, al
	jz .len_found_str
	inc rcx
	jmp .find_len_str

.len_found_str:
	mov rdx, rcx
	mov rax, 1
	mov rdi, 1
	syscall
	ret
;	--------------------


fn:
;	---Protocole d'entree---
	push rbp
	mov rbp, rsp
	sub rsp, 8
;	------------------------


	; Unary negation
	mov rax, rbp
	mov rax, [rax]
	mov rax, [rax - 8]
	mov rax, [rax + 0*8]
	push rax
	pop rax
	neg rax
	push rax
	mov rax, 3
	push rax
	mov rax, rbp
	mov rax, [rax]
	mov rax, [rax - 8]
	mov rax, [rax + 3*8]
	push rax

	; Performing * operation
	pop rbx
	pop rax
	imul rax, rbx
	push rax

	; Performing + operation
	pop rbx
	pop rax
	add rax, rbx
	push rax
	mov [rbp - 8], rax

	; print: parameter 1 (c)
	mov rax, [rbp - 8]
	call print_rax

	; print: end of line
	mov rax, 1
	mov rdi, 1
	mov rsi, newline
	mov rdx, 1
	syscall


;	---Protocole de sortie---
	pop rax
	mov rsp, rbp
	pop rbp
	ret
;	------------------------


f:
;	---Protocole d'entree---
	push rbp
	mov rbp, rsp
;	------------------------


	; print: parameter 1 (a)
	mov rax, rbp
	mov rax, [rax]
	mov rax, [rax - 8]

	; Affichage de la liste a
	mov rsi, rax
	mov rcx, [concat_list_a_len]
	mov rax, 1
	mov rdi, 1
	mov rdx, 1
	push rsi
	push rcx
	mov rsi, open_bracket_a
	syscall
	pop rcx
	pop rsi
	mov rdx, rcx

print_list_a_loop:
	test rcx, rcx
	jz print_list_a_end
	mov rax, [rsi]
	push rsi
	push rcx
	push rdx
	mov rbx, rdx
	sub rbx, rcx
	cmp rbx, 0
	jne skip_type_0_a
	call print_rax
	jmp print_list_a_loop_next
skip_type_0_a:
	cmp rbx, 1
	jne skip_type_1_a
	call print_rax
	jmp print_list_a_loop_next
skip_type_1_a:
	cmp rbx, 2
	jne skip_type_2_a
	call print_rax
	jmp print_list_a_loop_next
skip_type_2_a:
	cmp rbx, 3
	jne skip_type_3_a
	call print_rax
	jmp print_list_a_loop_next
skip_type_3_a:
	call print_rax
print_list_a_loop_next:
	pop rdx
	pop rcx
	pop rsi
	dec rcx
	test rcx, rcx
	jz print_list_a_loop_advance
	push rsi
	push rcx
	push rdx
	mov rax, 1
	mov rdi, 1
	mov rsi, comma_space
	mov rdx, 2
	syscall
	pop rdx
	pop rcx
	pop rsi
print_list_a_loop_advance:
	add rsi, 8
	jmp print_list_a_loop
print_list_a_end:
	mov rax, 1
	mov rdi, 1
	mov rsi, close_bracket_a
	mov rdx, 1
	syscall

	; print: end of line
	mov rax, 1
	mov rdi, 1
	mov rsi, newline
	mov rdx, 1
	syscall


;	---Protocole de sortie---
	mov rsp, rbp
	pop rbp
	ret
;	------------------------


_start:
	; Allocating space for 2 variable(s) & 2 function(s)
	push rbp
	mov rbp, rsp
	sub rsp, 32


	; Concatenation : a = liste concaténée
	mov rax, concat_list_a
	mov [rbp - 8], rax

;	---Stacking parameters---
	push rbp

;	---Calling the function---
	call fn
;	--------------------
	mov [rbp - 16], rax

;	---Stacking parameters---
	push rbp

;	---Calling the function---
	call f
;	--------------------

	; print: parameter 1 (x)
	mov rax, [rbp - 16]
	call print_rax

	; print: end of line
	mov rax, 1
	mov rdi, 1
	mov rsi, newline
	mov rdx, 1
	syscall



;	---End of program---
	mov rax, 60
	xor rdi, rdi 
	syscall
;	--------------------


; EOF