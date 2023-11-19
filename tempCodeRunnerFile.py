label_font = tkFont.Font(family="Inter", weight="bold", size=18)
label_font1 = tkFont.Font(family="Inter", size=14)

label = tk.Label(frame, text="Chat Log Analyst", font=label_font)
label.grid(row=0, column=0, columnspan=6)

label3 = tk.Label(frame, text="Host's name: ", font=label_font1)
label3.grid(row=1, column=0)

host_field = tk.Entry(frame, width=30)
host_field.grid(row=1, column=1)

submit_btn = tk.Button(frame, text="Submit", command=on_submit)
submit_btn.grid(row=1, column=2)

text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, width=60, height=20)
text.grid(row=2, column=0, rowspan=3, columnspan=3, padx=20)

chat_btn = tk.Button(frame, text="Load Chat Log", command=add_chat)
chat_btn.grid(row=5, column=0, columnspan=3, pady=10)

kywrd_text = scrolledtext.ScrolledText(
    frame, wrap=tk.WORD, width=60, height=5)
kywrd_text.grid(row=6, column=0, columnspan=3)

key_btn = tk.Button(frame, text="Add Keywords", command=add_keywords)
key_btn.grid(row=7, column=0, columnspan=3, pady=10)

scoreTable = ttk.Treeview(frame, columns=("Name", "Score"), show="headings")
scoreTable.heading("Name", text="Name")
scoreTable.heading("Score", text="Score")
scoreTable.column("Name", width=120)
scoreTable.column("Score", width=60)
scoreTable.grid(row=2, column=3, columnspan=2)

error = tk.Label(frame, text="", fg="red")
error.grid(row=10, column=0, columnspan=10, sticky="ew")