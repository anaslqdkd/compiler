section .data
	list_b dq 1, 0
	list_b_len dq 2
	open_bracket_b db "["
	comma_space db ", "
	close_bracket_b db "]"
	newline db 0xA
	minus_sign db "-"

section .bss
	buffer resb 20


section .text
	global _start


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


_start:
	; Allocating space for 2 variable(s) & 0 function(s)
	push rbp
	mov rbp, rsp
	sub rsp, 16

	mov rax, 5
	mov [rbp - 8], rax

	; b = [1, a]
	; Mise à jour de l'élément 1 avec la valeur de a
	mov rax, [rbp - 8]
	mov [list_b + 8], rax
	mov rax, list_b
	mov [rbp - 16], rax

	; print: parameter 1 (b)
	mov rax, [rbp - 16]

	; Affichage de la liste b
	mov rsi, rax
	mov rcx, [list_b_len]
	mov rax, 1
	mov rdi, 1
	mov rdx, 1
	push rsi
	push rcx
	mov rsi, open_bracket_b
	syscall
	pop rcx
	pop rsi
	mov rdx, rcx

print_list_b_loop:
	test rcx, rcx
	jz print_list_b_end
	mov rax, [rsi]
	push rsi
	push rcx
	push rdx
	mov rbx, rdx
	sub rbx, rcx
	cmp rbx, 0
	jne skip_type_0_b
	call print_rax
	jmp print_list_b_loop_next
skip_type_0_b:
	cmp rbx, 1
	jne skip_type_1_b
	call print_rax
	jmp print_list_b_loop_next
skip_type_1_b:
	call print_rax
print_list_b_loop_next:
	pop rdx
	pop rcx
	pop rsi
	dec rcx
	test rcx, rcx
	jz print_list_b_loop_advance
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
print_list_b_loop_advance:
	add rsi, 8
	jmp print_list_b_loop
print_list_b_end:
	mov rax, 1
	mov rdi, 1
	mov rsi, close_bracket_b
	mov rdx, 1
	syscall

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