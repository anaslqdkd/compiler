section .data
	cst_1 dd 3
	cst_2 dd 1
	cst_3 dd 2
	cst_4 dd 10
	cst_5 dd 8
	cst_6 dd 0
	cst_7 dd 5


section .text
	global _start
	global sans_param
	global feur
	global main
	global fr


_start:

;	---End of program---
	mov rax, 60
	xor rdi, rdi 
	syscall
;	------------------------
	mov dword [rbp+8], 3
sans_param:

;	---Protocole d'entrée---
	push rbp
	mov rbp, rsp
;	------------------------


;	---Protocole de sortie---
	pop rbp
	ret
;	------------------------

feur:

;	---Protocole d'entrée---
	push rbp
	mov rbp, rsp
;	------------------------

	mov dword [rbp+8], 5
	mov dword [rbp+8], 1

;	---Protocole de sortie---
	pop rbp
	ret
;	------------------------

main:

;	---Protocole d'entrée---
	push rbp
	mov rbp, rsp
;	------------------------


;	---Protocole de sortie---
	pop rbp
	ret
;	------------------------

fr:

;	---Protocole d'entrée---
	push rbp
	mov rbp, rsp
;	------------------------


;	---Protocole de sortie---
	pop rbp
	ret
;	------------------------

; EOF