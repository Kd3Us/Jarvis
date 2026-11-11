def get_n_exchange_history(history:list, n:int)->list:
    
    if len(history) < n:
        return history
    else:
        return history[-n*2:]
    
if __name__ == "__main__":
    history_test_less_3 = [
        {
            "role":"user",
            "content":"test1"
        },
        {
            "role":"assistant",
            "content":"test1"
        },
        {
            "role":"user",
            "content":"test2"
        },
        {
            "role":"assistant",
            "content":"test2"
        }
    ]

    history_test_more_3 =  [
        {
            "role":"user",
            "content":"test1"
        },
        {
            "role":"assistant",
            "content":"test1"
        },
        {
            "role":"user",
            "content":"test2"
        },
        {
            "role":"assistant",
            "content":"test2"
        },
        {
            "role":"user",
            "content":"test3"
        },
        {
            "role":"assistant",
            "content":"test3"
        },
        {
            "role":"user",
            "content":"test4"
        },
        {
            "role":"assistant",
            "content":"test4"
        },
        {
            "role":"user",
            "content":"test5"
        },
        {
            "role":"assistant",
            "content":"test5"
        }
    ]

    print(get_n_exchange_history(history_test_less_3,3))
    print(get_n_exchange_history(history_test_more_3,3))