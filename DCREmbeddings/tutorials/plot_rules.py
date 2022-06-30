def get_plots_from_df_degree(df_rules):
    """Given a dataframe with metric values, return plot with error bars"""
    number_pairs = []
    error_list_low = []
    error_list_high= []
    for index,row in df_rules.iterrows():
        OR = row['causal_metric']
        ICL = row['causal_metric_IC'][0]
        ICP = row['causal_metric_IC'][1]
        error_list_low.append(OR-ICL)
        error_list_high.append(ICP-OR)
        number_pairs.append(row['Number_Pairs'])
    error_list = [error_list_low,error_list_high]

    list_to_plot_tr = list(df_rules['Degree'])
    list_odds = list(df_rules['causal_metric'])

    fig = plt.figure(figsize=(20,6))
    ax = fig.add_subplot(111)
    ax.set_ylim([0, 5])
    ax.set_xlim([-0.5,max(list_to_plot_tr)+0.5])
    
    ax.scatter(list_to_plot_tr,list_odds,c='black')
    ax.errorbar(list_to_plot_tr,list_odds,yerr=error_list,fmt="o",c='black')
    ax.axhline(y = 1, color = 'red', linestyle = '-')

    axB = ax.twinx()
    axB.bar(list_to_plot_tr, number_pairs, width=0.75, fill=False,color='blue')
    
    plt.xticks(list_to_plot_tr)

    plt.title("causal_T given number of differences")
    plt.show()
