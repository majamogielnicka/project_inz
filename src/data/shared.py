def get_initial_state(prices: list[int], order: int, offset: int | None = None)-> list[int]:
    "return last prices"
    initial_state_vector = []
    
    for i in range(order):
        i+=1
        if offset is None:
            initial_state_vector.append(prices[-i])
        else:
            initial_state_vector.append(prices[-i-offset])


    return initial_state_vector

if __name__ == "__main__":
    prices = [1,2,3,4,5,6,7,8,9,10,11,12]
    horizont = 3 
    r =2
    print(get_initial_state(prices, 3, 2))
    print(get_initial_state(prices, 3))